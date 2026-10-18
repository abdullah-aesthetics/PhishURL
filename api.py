"""PhishURL REST API (used by the Chrome extension).   Run:  uvicorn api:app --port 8000
Docs: http://localhost:8000/docs"""
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from phishurl.model import load_model, score_url, train_and_save
from phishurl.sample import generate

ROOT = Path(__file__).parent
MODELS = ROOT / "models"
if not (MODELS / "model.joblib").exists():
    data = ROOT / "data" / "urls.csv"
    if not data.exists():
        data = ROOT / "data" / "sample_urls.csv"
        if not data.exists():
            generate(data)
    train_and_save(data, MODELS)
bundle = load_model(MODELS)

app = FastAPI(title="PhishURL API", version="1.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


class ScanRequest(BaseModel):
    url: str


@app.get("/health")
def health():
    return {"status": "ok", "model": bundle["best"]}


@app.post("/scan")
def scan(req: ScanRequest):
    r = score_url(req.url, bundle)
    return {"url": r["url"], "verdict": r["verdict"], "level": r["level"], "risk": round(r["risk"], 4),
            "ml_probability": round(r["ml_probability"], 4),
            "reasons": [{"severity": s, "text": t} for s, t in r["reasons"]]}
