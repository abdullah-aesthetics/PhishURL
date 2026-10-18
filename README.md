# 🔗 PhishURL - Phishing URL and Message Scanner

Detects phishing links (and links hidden in SMS/WhatsApp messages) from the URL text alone. Nothing is ever visited.
Companion to [PhishGuard](https://github.com/aroojfatimah399/PhishGuard) (email text detection).

**Live demo:** [ADD URL] · **Report:** [ADD LINK] · **Video:** [ADD LINK]

## Features
- URL scanner: verdict, ML probability, rule score, combined risk gauge and plain-English reasons
- Message scanner: finds links in a pasted SMS, scores each one and lists scam wording
- 21 lexical URL features; Random Forest vs Logistic Regression (5-fold CV + hold-out test)
- Performance tab: metrics, feature importances, confusion matrices

## Setup (Windows)
```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m pytest -q
streamlit run app.py
```
The app trains on a **synthetic** demo set the first time. Its scores are unrealistically high, so do not report them.

## Use a real dataset
Download a labelled URL list (e.g. a Kaggle "phishing URLs" dataset, PhishTank/OpenPhish for phishing and the Tranco list for legitimate),
save it as `data/urls.csv` with columns `url,label` (label: phishing/bad/1 or legitimate/good/0), then:
```
python train.py
```
Commit the new `models/` folder before deploying.

## Structure
`app.py` dashboard · `train.py` training · `phishurl/` features, model, sample data · `tests/` pytest

## Report checklist
Overview and objectives · features and technologies · setup · usage and screenshots · architecture
(URL -> features -> models -> risk score -> dashboard) · results (real dataset) · challenges · future work · conclusion · references.

## Future work
FastAPI backend, Chrome extension calling it, SMS text classifier (UCI SMS Spam Collection), DistilBERT comparison,
WHOIS/domain-age and blocklist lookups.

## Chrome extension + API (PhishURL Shield)
1. Start the API: `uvicorn api:app --port 8000` (interactive docs at http://localhost:8000/docs).
2. In Chrome open `chrome://extensions`, switch on **Developer mode**, click **Load unpacked** and choose the `extension` folder.
3. Browse normally: the toolbar badge shows **OK** (green), **!** (amber) or **!!** (red) for every page. Click the icon for the verdict and reasons.

The extension only sends the page URL to your own local API, never the page content. The Streamlit app is deployed online;
the API and extension run locally, so show them in your demo video.

## Demo video script (3-4 min)
1. Hero + URL scanner with the phishing example, then a legitimate one. 2. Message scanner with an SMS. 3. Batch scan with a CSV.
4. Performance tab. 5. Start the API, load the extension, visit a safe site and show the badge, then open `/docs` and scan a bad URL.
