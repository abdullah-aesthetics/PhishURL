# 🔗 PhishURL - Phishing URL and Message Scanner

**Student:** Muhammad Abdullah Aamir

| | |
|---|---|
| 🌐 **Live demo** | https://phishurl-abdullah.streamlit.app/ |
| 📄 **Final report** | [Project Report (PDF)](docs/Project_Report.pdf) |
| 💻 **Source code** | https://github.com/abdullah-aesthetics/PhishURL |
| 📊 **Dataset** | [Phishing Url by Hemanth Pingali (Kaggle)](https://www.kaggle.com/datasets/hemanthpingali/phishing-url) |

## Project Overview
Phishing links imitate trusted services to steal passwords, card details and money. PhishURL analyses the **text of a
URL alone** and predicts whether it is legitimate or phishing. It gives a **risk score** and **plain-English reasons**,
and it **never opens or visits the link**, so scanning a malicious URL cannot harm you.

The same models power three interfaces: a **Streamlit dashboard** (URL, message and batch scanners), a **REST API**
and a **Chrome extension** that shows a warning badge while you browse.
PhishURL is the companion to PhishGuard, which detects phishing from email text. Together they cover emails and links.

## Objectives
1. Build and compare machine-learning classifiers that detect phishing URLs from the URL text only.
2. Make every decision explainable with a risk score and readable reasons.
3. Evaluate honestly with a stratified hold-out test set and cross-validation, and report weaknesses as well as strengths.
4. Deliver a deployed dashboard, a REST API and a browser extension, backed by tests and documentation.

## Features
- **URL scanner:** verdict, ML probability, rule score, animated risk gauge and reasons for each URL
- **Message scanner:** paste an SMS or WhatsApp message; links are found, scored one by one, and scam wording is listed
- **Batch scanner:** scan many URLs (pasted or CSV) with summary cards, a risk chart and a results download
- **Three models compared:** Random Forest, character n-gram Logistic Regression, and a Hybrid of both feature types
- **Performance dashboard:** accuracy, precision, recall, F1, ROC-AUC, feature importances and confusion matrices
- **REST API** (FastAPI) with interactive documentation
- **Chrome extension (PhishURL Shield):** toolbar badge (OK, !, !!) and a popup with the verdict and reasons
- Session history and automated unit tests

## Technologies
Python · scikit-learn · pandas · Streamlit · Altair · FastAPI · Uvicorn · JavaScript (Chrome Manifest V3) · joblib · pytest · Git / GitHub · Streamlit Community Cloud

## System Workflow / Architecture
```
TRAINING (offline)
Dataset (11,429 URLs) -> Clean labels, remove duplicates -> Stratified 80/20 split
  -> 21 URL features + character n-grams (2-5) -> Random Forest | n-gram LR | Hybrid
  -> 5-fold CV + hold-out test -> best model by CV F1 -> saved with joblib

ANALYSIS (live)
URL or SMS link (dashboard, API or extension) -> extract features and n-grams
  -> ML probability + rule-based reasons -> Risk = 0.8 x ML + 0.2 x rules
  -> verdict, gauge and reasons (dashboard) / JSON (API) / badge and popup (extension)
```
**Risk score:** `0.8 × ML probability + 0.2 × rule score`. The rule score is the sum of reason weights
(high = 3, medium = 2, low = 1) divided by 8 and capped at 1. Levels: Low < 0.35 ≤ Medium < 0.65 ≤ High.
The verdict follows the ML probability at a 0.5 threshold.

## Installation and Setup
Requires Python 3.10+ and Git (Chrome for the extension). Commands are for Windows PowerShell.
```powershell
git clone https://github.com/abdullah-aesthetics/PhishURL.git
cd PhishURL
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m streamlit run app.py
```
The dashboard opens at http://localhost:8501. A trained model is included, so it runs immediately.
If `streamlit` is not recognised, keep using `python -m streamlit`.
On macOS/Linux use `python3 -m venv .venv && source .venv/bin/activate`.

**Retrain on the dataset**
1. Download the two files from Kaggle (`Training.parquet`, `Testing.parquet`) and put them in the project folder.
2. Convert them to the CSV the trainer expects (`url`, `label`):
```python
import pandas as pd
tr, te = pd.read_parquet("Training.parquet"), pd.read_parquet("Testing.parquet")
df = pd.concat([tr, te])[["url", "status"]].rename(columns={"status": "label"}).drop_duplicates("url")
df["label"] = df["label"].map({"phishing": 1, "legitimate": 0})
df.to_csv("data/urls.csv", index=False)
```
3. Train and test:
```powershell
python train.py
python -m pytest -q
```

## REST API
```powershell
python -m uvicorn api:app --port 8000
```
Interactive documentation: http://localhost:8000/docs. Example request:
```powershell
curl.exe -X POST http://localhost:8000/scan -H "Content-Type: application/json" -d "{\"url\": \"http://paypal-secure-login.top/verify\"}"
```
The response contains `verdict`, `level`, `risk`, `ml_probability` and a list of `reasons`.

## Chrome Extension (PhishURL Shield)
1. Start the API as shown above and keep it running.
2. In Chrome open `chrome://extensions` and switch on **Developer mode**.
3. Click **Load unpacked** and choose the `extension` folder.
4. Browse normally: the badge shows **OK** (green), **!** (amber) or **!!** (red). Click the icon for the verdict and reasons.

Only the page URL is sent, to your own local API, never the page content. The dashboard is hosted online, but the API
and extension run locally, so they are shown in the demo video.

## Usage
1. **URL scanner:** paste a link or click an example in the sidebar, then press **Scan URL**.
2. **Message scanner:** paste an SMS or WhatsApp message and press **Scan message**.
3. **Batch scan:** paste one URL per line or upload a CSV with a `url` column.
4. **Model performance:** metrics, feature importances and confusion matrices.
5. Use the sidebar to switch between the three models.

### Screenshots

**Live deployment on Streamlit Cloud**

![Live app](docs/screenshots/Screenshot%202026-10-18%20124106.png)

**Home page and URL scanner**

![Home](docs/screenshots/Screenshot%202026-10-18%20121018.png)

**Phishing URL: High risk with reasons**

![Phishing result](docs/screenshots/Screenshot%202026-10-18%20121054.png)

**Legitimate URL: Low risk**

![Legitimate result](docs/screenshots/Screenshot%202026-10-18%20121117.png)

**Session history**

![Session history](docs/screenshots/Screenshot%202026-10-18%20121254.png)

**Message scanner (parcel scam SMS)**

![Message scanner](docs/screenshots/Screenshot%202026-10-18%20121408.png)

**Batch scan**

![Batch scan](docs/screenshots/Screenshot%202026-10-18%20121613.png)

**Model performance**

![Model performance](docs/screenshots/Screenshot%202026-10-18%20121706.png)

**Confusion matrices**

![Confusion matrices](docs/screenshots/Screenshot%202026-10-18%20121737.png)

**REST API documentation**

![API docs](docs/screenshots/Screenshot%202026-10-18%20121824.png)

**API scan request and response**

![API scan](docs/screenshots/Screenshot%202026-10-18%20121918.png)

**Extension on a safe site (green badge)**

![Extension safe](docs/screenshots/Screenshot%202026-10-18%20122004.png)

**Extension on a suspicious page (red badge)**

![Extension flagged](docs/screenshots/Screenshot%202026-10-18%20122131.png)

## Dataset
**Phishing Url - A Dataset for Phishing Detection** by Hemanth Pingali (Kaggle), licence CC BY-NC-SA 4.0
(non-commercial use). Two Parquet files with the URL, 87 pre-computed features and a status label.

| Item | Value |
|---|---|
| Training.parquet + Testing.parquet | 7,658 + 3,772 rows |
| After combining and removing 1 duplicate | **11,429 URLs** |
| Legitimate / phishing | 5,715 / 5,714 (balanced) |
| Train / test split used | 9,143 / 2,286 (stratified 80/20) |

Only the URL and label are used. The dataset's other 87 features (page content, WHOIS, traffic, Google index) need the
page or external services, so a scanner that never opens the link cannot compute them for a new URL. PhishURL computes
its own features from the URL text. Kaggle does not name the dataset's original source, so its provenance is unverified.

## Testing and Results
**Method:** 5-fold stratified cross-validation on the training set, then one evaluation on the untouched test set
(2,286 URLs). The text vectoriser is inside each pipeline, so there is no data leakage. The default model is chosen
by cross-validated F1, never by test score.

| Metric | Random Forest (21 features) | Char n-gram + LR | Hybrid (n-gram + features) |
|---|---|---|---|
| Accuracy | 0.851 | 0.935 | 0.934 |
| Precision | 0.864 | 0.939 | 0.947 |
| Recall | 0.834 | 0.931 | 0.919 |
| F1-score | 0.849 | 0.935 | 0.933 |
| ROC-AUC | 0.926 | 0.982 | 0.984 |
| CV F1 (mean ± std) | 0.848 ± 0.006 | 0.932 ± 0.006 | 0.932 ± 0.005 |

**Confusion matrices (test set)**

| Model | Legitimate correct | False alarms | Phishing missed | Phishing caught |
|---|---|---|---|---|
| Random Forest | 993 | 150 | 190 | 953 |
| Char n-gram + LR | 1,074 | 69 | 79 | 1,064 |
| Hybrid | 1,084 | 59 | 93 | 1,050 |

**Discussion:** character n-grams lift accuracy from about 85% (hand-built features only) to about 93.5%. The Hybrid
model is the default: it ties the n-gram model on CV F1 and has the highest precision (fewest false alarms) and AUC.
The difference between the two top models is within one standard deviation.

**Realistic accuracy:** about a third of the test URLs share a website with the training data. In a separate one-off
check on test URLs from websites never seen in training, the n-gram models scored about 91%, a more honest estimate for new sites.

**Manual testing of the deployed app:** 8 of 10 correct. The fake PayPal link (100%), IP-address link (97.5%), shortener
link (90%) and parcel-scam SMS (99%) were flagged; github.com, wikipedia.org, bbc.co.uk and tapmad.com scored low.
Two genuine services were **wrongly flagged**: `mail.google.com/mail/u/0/#inbox` (78.5%) and
`printify.com/app/auth/login` (75.7%), because words like login, auth and inbox resemble phishing patterns.

**Software tests:** 2 pytest tests (feature extraction and reasons; training and scoring) pass.
```powershell
python -m pytest -q
```

## Challenges
- The first 21 hand-built features gave only about 85%; adding character n-grams fixed this
- The dataset's strongest features cannot be computed for a live, never-visit scanner
- False positives on genuine login and inbox pages
- The same websites appear in training and test data, which inflates accuracy
- Converting Parquet files with text labels into a clean binary dataset
- Pinning library versions so the deployed model loads without warnings
- Linking the repository and the Streamlit deployment to the same GitHub account
- The extension needs a local API, so it is demonstrated locally and in the video

## Limitations
URL text only: no page content, domain age, reputation, redirects or blocklists. It can miss phishing links that
look ordinary and flag genuine links that look unusual. Expect about 91% accuracy on new websites. Use it as decision
support, not as the only defence.

## Future Improvements
- Allow-list of well-known domains and domain-reputation lookups to cut false positives
- Domain age / WHOIS data, blocklist checks (PhishTank, OpenPhish) and redirect resolution
- An SMS text classifier (for example the UCI SMS Spam Collection) combined with the link score
- DistilBERT comparison trained in Google Colab
- Domain-grouped evaluation and a second independent dataset
- Host the API online so the extension works without a local server
- Explain decisions with n-gram coefficients or SHAP

## Project Structure
```
app.py             Streamlit dashboard
api.py             FastAPI service used by the extension
train.py           Train and evaluate; writes models/
phishurl/          features.py (URL features and reasons) · model.py (training, scoring) · sample.py (demo data)
extension/         Chrome extension (manifest.json, background.js, popup.html, popup.js)
models/            model.joblib, metrics.json
tests/             pytest suite
docs/              PhishURL_Final_Report.pdf, screenshots/
.streamlit/        Dark theme configuration
```

## Conclusion
Phishing links can be detected from the URL text alone with about 93.5% accuracy on a held-out test set
(about 91% on unseen websites), and every decision can be explained. The project delivers three models, a deployed
dashboard, a REST API and a browser extension, with tests and public source code.

## References
1. Pingali, H. *Phishing Url: A Dataset for Phishing Detection*. Kaggle. https://www.kaggle.com/datasets/hemanthpingali/phishing-url (CC BY-NC-SA 4.0)
2. Hannousse, A. and Yahiouche, S. (2021). Towards benchmark datasets for machine learning based website phishing detection. *Engineering Applications of Artificial Intelligence*, 104, 104347. (Possible origin of the dataset schema; unverified.)
3. Pedregosa, F. et al. (2011). Scikit-learn: Machine Learning in Python. *JMLR*, 12, 2825-2830.
4. Streamlit documentation. https://docs.streamlit.io
5. FastAPI documentation. https://fastapi.tiangolo.com
6. Chrome Extensions (Manifest V3). https://developer.chrome.com/docs/extensions
7. Anti-Phishing Working Group. Phishing Activity Trends Reports. https://apwg.org
