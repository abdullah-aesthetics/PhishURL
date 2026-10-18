"""python train.py [--data data/urls.csv]   (CSV needs columns: url, label)"""
import argparse
from pathlib import Path

from phishurl.model import train_and_save
from phishurl.sample import generate

ROOT = Path(__file__).parent


def default_data():
    real, sample = ROOT / "data" / "urls.csv", ROOT / "data" / "sample_urls.csv"
    if real.exists():
        return real
    if not sample.exists():
        generate(sample)
    return sample


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--data", default=str(default_data()))
    a = ap.parse_args()
    m = train_and_save(a.data, ROOT / "models")
    print(f"{m['n_total']} URLs ({m['n_phishing']} phishing / {m['n_legit']} legitimate), test set {m['n_test']}")
    for n, r in m["models"].items():
        t = r["test"]
        print(f"{n:20s} CV-F1 {r['cv_f1'][0]:.3f} | acc {t['accuracy']:.3f} prec {t['precision']:.3f} rec {t['recall']:.3f} F1 {t['f1']:.3f} AUC {t['roc_auc']:.3f}")
    print("Best model:", m["best"])
