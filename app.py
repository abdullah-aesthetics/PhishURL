"""PhishURL - Streamlit dashboard.   Run:  streamlit run app.py"""
import html
import json
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

from phishurl.features import URL_RE
from phishurl.model import load_model, score_url, train_and_save
from phishurl.sample import generate

ROOT, MODELS = Path(__file__).parent, Path(__file__).parent / "models"
COL = {"Low": "#3dffa0", "Medium": "#ffb020", "High": "#ff4d5e"}
SEV = {"high": "#ff4d5e", "medium": "#ffb020", "low": "#ffe08a"}
SMISH = ["urgent", "verify", "suspended", "locked", "claim", "prize", "winner", "refund", "otp", "click", "bank", "parcel", "customs", "free"]
st.set_page_config(page_title="PhishURL", page_icon="🔗", layout="wide")
st.markdown("""<style>
.block-container{padding-top:1.4rem;max-width:1150px}#MainMenu,footer{visibility:hidden}
.hero{padding:1.6rem 2rem;border:1px solid rgba(61,255,160,.25);border-radius:16px;background:radial-gradient(circle at 90% 10%,rgba(61,255,160,.12),transparent 45%),#0d151c;margin-bottom:1rem}
.hero h1{margin:0;font-size:2.6rem}.hero span{color:#3dffa0}.hero p{opacity:.75;margin:.4rem 0 0}
.card{background:#111a21;border:1px solid rgba(255,255,255,.08);border-radius:14px;padding:.9rem 1.1rem;margin-bottom:.7rem}
.stat{text-align:center}.stat b{display:block;font-size:1.6rem}.stat span{opacity:.6;font-size:.72rem;text-transform:uppercase;letter-spacing:.1em}
.gauge{display:block;margin:0 auto;max-width:280px}.gauge .arc{animation:fill 1.3s ease-out forwards}@keyframes fill{from{stroke-dashoffset:251.3}}
.scanbar{height:3px;margin-top:1rem;background:linear-gradient(90deg,transparent,#3dffa0,transparent);box-shadow:0 0 14px #3dffa0;animation:sl 2.6s ease-in-out infinite}
@keyframes sl{0%{transform:translateX(-60%)}100%{transform:translateX(60%)}}
.card{transition:transform .2s,border-color .2s}.card:hover{transform:translateY(-3px);border-color:rgba(61,255,160,.45)}
</style>""", unsafe_allow_html=True)


@st.cache_resource(show_spinner="Loading model (training on first run)...")
def bundle():
    if not (MODELS / "model.joblib").exists():
        data = ROOT / "data" / "urls.csv"
        if not data.exists():
            data = ROOT / "data" / "sample_urls.csv"
            if not data.exists():
                generate(data)
        train_and_save(data, MODELS)
    return load_model(MODELS)


def stat(v, l):
    return f'<div class="card stat"><b>{v}</b><span>{l}</span></div>'


def gauge(score, level):
    c, arc = COL[level], "M20 100 A80 80 0 0 1 180 100"
    return (f'<svg class="gauge" viewBox="0 0 200 125"><path d="{arc}" fill="none" stroke="rgba(255,255,255,.1)" stroke-width="16" stroke-linecap="round"/>'
            f'<path class="arc" d="{arc}" fill="none" stroke="{c}" stroke-width="16" stroke-linecap="round" stroke-dasharray="251.3" style="stroke-dashoffset:{251.3 * (1 - min(score, 1)):.1f}"/>'
            f'<text x="100" y="92" text-anchor="middle" font-size="34" font-weight="800" fill="{c}">{score:.0%}</text>'
            f'<text x="100" y="114" text-anchor="middle" font-size="10" letter-spacing="2" fill="#8a9a92">RISK SCORE</text></svg>')


def show(r):
    c1, c2 = st.columns([1, 1.3], gap="large")
    with c1:
        st.markdown(f'<div class="card">{gauge(r["risk"], r["level"])}<p style="text-align:center;font-size:1.4rem;font-weight:700;color:{COL[r["level"]]};margin:0">{r["verdict"]}</p>'
                    f'<p style="text-align:center;opacity:.7;margin:.2rem 0 0">{r["level"]} risk</p></div>', unsafe_allow_html=True)
        a, b = st.columns(2)
        a.markdown(stat(f'{r["ml_probability"]:.0%}', "ML probability"), unsafe_allow_html=True)
        b.markdown(stat(f'{r["rule_score"]:.0%}', "Rule score"), unsafe_allow_html=True)
    with c2:
        st.markdown("**Why this verdict?**")
        if not r["reasons"]:
            st.success("No suspicious URL patterns found.")
        for sev, txt in r["reasons"]:
            st.markdown(f'<div class="card" style="border-left:4px solid {SEV[sev]}"><b style="color:{SEV[sev]}">{sev.upper()}</b> &nbsp;{html.escape(txt)}</div>', unsafe_allow_html=True)
        with st.expander("Extracted features"):
            st.dataframe(pd.Series(r["features"], name="value"), width="stretch")


b = bundle()
metrics = json.loads((MODELS / "metrics.json").read_text())
st.markdown('<div class="hero"><h1>Phish<span>URL</span></h1><p>Paste a link or an SMS. Get a verdict, a risk score and the reasons behind it. Nothing is ever opened or visited.</p><div class="scanbar"></div></div>', unsafe_allow_html=True)
with st.sidebar:
    st.markdown("### 🔗 Control panel")
    model = st.selectbox("Model", list(b["models"]), index=list(b["models"]).index(b["best"]))
    if "sample_urls" in metrics["data"]:
        st.warning("Trained on the synthetic demo dataset. Retrain on real data (see README).")
    st.markdown("**Examples**")
    for label, u in {"🚨 Fake PayPal login": "http://paypal-secure-login.top/verify/account.php?id=88231&session=4412",
                     "🚨 IP address link": "http://192.168.44.12/signin/update.php?id=991",
                     "✅ GitHub": "https://github.com", "✅ Wikipedia": "https://en.wikipedia.org/wiki/Phishing"}.items():
        st.button(label, on_click=lambda v=u: st.session_state.update(url=v), width="stretch")

t1, t2, tb, t3, t4 = st.tabs(["🔗 URL scanner", "💬 Message scanner", "📂 Batch scan", "📊 Model performance", "ℹ️ About"])
with t1:
    url = st.text_input("URL to check", key="url", placeholder="https://example.com/login")
    if st.button("🔎 Scan URL", type="primary") and url.strip():
        r = score_url(url, b, model)
        st.session_state.setdefault("hist", []).append({"URL": url[:60], "Verdict": r["verdict"], "Risk": r["risk"]})
        st.toast(f"{r['verdict']} - {r['level']} risk", icon="🚨" if r["level"] == "High" else "✅")
        show(r)
    if st.session_state.get("hist"):
        st.markdown("#### Session history")
        st.dataframe(pd.DataFrame(st.session_state["hist"][::-1]), hide_index=True, width="stretch",
                     column_config={"Risk": st.column_config.ProgressColumn("Risk", min_value=0, max_value=1, format="percent")})
with t2:
    msg = st.text_area("Paste an SMS / WhatsApp message", height=140, key="msg",
                       placeholder="Your parcel is held. Pay the customs fee now: http://dhl-track.xyz/pay")
    if st.button("🔎 Scan message", type="primary") and msg.strip():
        links = URL_RE.findall(msg)
        words = [w for w in SMISH if w in msg.lower()]
        st.markdown(f"**Scam wording found:** {', '.join(f'`{w}`' for w in words) or 'none'}  \n**Links found:** {len(links)}")
        for l in links:
            st.markdown(f"##### `{l}`")
            show(score_url(l, b, model))
        if not links:
            st.info("No links in this message. Scam wording alone is a weaker signal.")
with tb:
    st.write("Paste one URL per line, or upload a CSV with a **url** column.")
    txt = st.text_area("URLs", height=120, key="batch_txt")
    up = st.file_uploader("CSV file", type="csv")
    urls = [u.strip() for u in txt.splitlines() if u.strip()]
    if up:
        d = pd.read_csv(up)
        d.columns = [c.lower().strip() for c in d.columns]
        urls += d["url"].astype(str).tolist() if "url" in d.columns else []
    if urls and st.button("🔎 Scan all", type="primary"):
        rs = [score_url(u, b, model) for u in urls[:500]]
        out = pd.DataFrame([{"url": r["url"], "verdict": r["verdict"], "risk": round(r["risk"], 3), "level": r["level"],
                             "reasons": "; ".join(t for _, t in r["reasons"])} for r in rs])
        c1, c2, c3 = st.columns(3)
        c1.markdown(stat(len(out), "URLs scanned"), unsafe_allow_html=True)
        c2.markdown(stat(int((out["level"] == "High").sum()), "High risk"), unsafe_allow_html=True)
        c3.markdown(stat(f"{out['risk'].mean():.0%}", "Average risk"), unsafe_allow_html=True)
        st.bar_chart(out["level"].value_counts().reindex(["Low", "Medium", "High"]).fillna(0), color="#3dffa0")
        st.dataframe(out, width="stretch", column_config={"risk": st.column_config.ProgressColumn("risk", min_value=0, max_value=1, format="percent")})
        st.download_button("⬇️ Download results CSV", out.to_csv(index=False), "phishurl_batch.csv", "text/csv")
with t3:
    k = st.columns(4)
    for col, (v, l) in zip(k, [(metrics["n_total"], "URLs"), (metrics["n_phishing"], "Phishing"), (metrics["n_legit"], "Legitimate"), (metrics["n_test"], "Test set")]):
        col.markdown(stat(f"{v:,}", l), unsafe_allow_html=True)
    rows = [{"Model": n, **{k_.title(): round(v, 4) for k_, v in r["test"].items()}, "CV F1": f"{r['cv_f1'][0]:.3f} ± {r['cv_f1'][1]:.3f}"} for n, r in metrics["models"].items()]
    st.dataframe(pd.DataFrame(rows).set_index("Model").T, width="stretch")
    imp = pd.DataFrame({"Feature": list(metrics["importances"]), "Importance": list(metrics["importances"].values())}).nlargest(10, "Importance")
    st.markdown("#### Most important features (Random Forest)")
    st.altair_chart(alt.Chart(imp).mark_bar(color="#3dffa0").encode(x="Importance:Q", y=alt.Y("Feature:N", sort="-x"), tooltip=["Feature", alt.Tooltip("Importance:Q", format=".3f")]), width="stretch")
    st.markdown("#### Confusion matrices (rows: actual, columns: predicted; order legitimate, phishing)")
    for col, (n, r) in zip(st.columns(len(metrics["models"])), metrics["models"].items()):
        col.markdown(f"**{n}**"); col.dataframe(pd.DataFrame(r["confusion_matrix"], index=["Legit", "Phish"], columns=["Legit", "Phish"]), width="stretch")
with t4:
    st.markdown("""**How it works:** 21 lexical features (length, IP host, subdomains, hyphens, entropy, sensitive words, brand mismatch, TLD, HTTPS ...) and
character n-grams of the URL text are extracted. Random Forest, an n-gram Logistic Regression and a hybrid estimate the phishing probability, and rule-based
checks add readable reasons. Risk = 0.8 × ML probability + 0.2 × rule score.

**Limitations:** lexical features only (no page content, WHOIS age or blocklist lookups), and accuracy depends on the training data.""")
