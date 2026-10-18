"""Train / evaluate / load URL classifiers (Random Forest vs Logistic Regression)."""
import json
from datetime import datetime
from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import StratifiedKFold, cross_validate, train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from .features import FEATURES, extract

PHISH = {"1", "phishing", "bad", "malicious", "phish", "true", "defacement", "malware"}
LEGIT = {"0", "legitimate", "good", "benign", "safe", "false"}


def load_urls(path) -> pd.DataFrame:
    df = pd.read_csv(path)
    df.columns = [c.lower().strip() for c in df.columns]
    ucol = next(c for c in ("url", "urls", "link") if c in df.columns)
    lcol = next(c for c in ("label", "type", "class", "status", "result") if c in df.columns)
    lab = df[lcol].astype(str).str.lower().str.strip().map(lambda s: 1 if s in PHISH else 0 if s in LEGIT else None)
    out = pd.DataFrame({"url": df[ucol].astype(str), "label": lab}).dropna().drop_duplicates("url")
    out["label"] = out["label"].astype(int)
    return out.reset_index(drop=True)


def featurize(urls) -> pd.DataFrame:
    d = pd.DataFrame([extract(u) for u in urls])[FEATURES]
    d["url"] = [str(u) for u in urls]
    return d


def _tfidf():
    return TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 5), min_df=3, sublinear_tf=True, max_features=100000)


def train_and_save(data_path, out_dir, seed=42) -> dict:
    out_dir = Path(out_dir); out_dir.mkdir(parents=True, exist_ok=True)
    df = load_urls(data_path)
    if df["label"].value_counts().min() < 20:
        raise ValueError("Need at least 20 URLs of each class.")
    X, y = featurize(df["url"]), df["label"]
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, stratify=y, random_state=seed)
    lr = lambda: LogisticRegression(max_iter=3000, C=5, class_weight="balanced")
    models = {
        "Random Forest": make_pipeline(ColumnTransformer([("n", "passthrough", FEATURES)]),
                                       RandomForestClassifier(100, min_samples_leaf=3, class_weight="balanced", random_state=seed, n_jobs=-1)),
        "Char n-gram + LR": make_pipeline(ColumnTransformer([("t", _tfidf(), "url")]), lr()),
        "Hybrid (n-gram + features)": make_pipeline(ColumnTransformer([("t", _tfidf(), "url"), ("n", StandardScaler(), FEATURES)]), lr()),
    }
    cv = StratifiedKFold(5, shuffle=True, random_state=seed)
    res, fitted = {}, {}
    for name, m in models.items():
        c = cross_validate(m, Xtr, ytr, cv=cv, scoring=["accuracy", "precision", "recall", "f1"])
        m.fit(Xtr, ytr)
        pred, proba = m.predict(Xte), m.predict_proba(Xte)[:, 1]
        res[name] = {"cv_f1": [float(c["test_f1"].mean()), float(c["test_f1"].std())],
                     "test": {"accuracy": accuracy_score(yte, pred), "precision": precision_score(yte, pred),
                              "recall": recall_score(yte, pred), "f1": f1_score(yte, pred), "roc_auc": roc_auc_score(yte, proba)},
                     "confusion_matrix": confusion_matrix(yte, pred).tolist()}
        res[name]["test"] = {k: float(v) for k, v in res[name]["test"].items()}
        fitted[name] = m
    best = max(res, key=lambda n: res[n]["cv_f1"][0])
    imp = dict(zip(FEATURES, map(float, fitted["Random Forest"][-1].feature_importances_)))
    metrics = {"trained_at": datetime.now().isoformat(timespec="seconds"), "data": str(data_path), "best": best,
               "n_total": len(df), "n_phishing": int(y.sum()), "n_legit": int((y == 0).sum()), "n_test": len(yte),
               "models": res, "importances": imp}
    joblib.dump({"models": fitted, "best": best}, out_dir / "model.joblib")
    (out_dir / "metrics.json").write_text(json.dumps(metrics, indent=2))
    return metrics


def load_model(model_dir):
    return joblib.load(Path(model_dir) / "model.joblib")


def score_url(url: str, bundle: dict, name=None) -> dict:
    from .features import reasons
    f = extract(url)
    p = float(bundle["models"][name or bundle["best"]].predict_proba(featurize([url]))[0, 1])
    rs = reasons(f)
    w = {"high": 3, "medium": 2, "low": 1}
    rule = min(1.0, sum(w[s] for s, _ in rs) / 8)
    risk = 0.8 * p + 0.2 * rule
    return {"url": url, "ml_probability": p, "rule_score": rule, "risk": risk, "features": f, "reasons": rs,
            "level": "Low" if risk < .35 else "Medium" if risk < .65 else "High", "verdict": "Likely phishing" if p >= .5 else "Likely legitimate"}
