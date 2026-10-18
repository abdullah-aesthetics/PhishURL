"""SYNTHETIC demo URLs so the app/tests run out of the box. Not a real dataset:
scores on it are unrealistically high. Train on PhishTank/Kaggle data for real results."""
import random
import pandas as pd

LEGIT = ["google.com", "wikipedia.org", "github.com", "amazon.com", "bbc.co.uk", "nytimes.com", "stackoverflow.com",
         "linkedin.com", "microsoft.com", "apple.com", "youtube.com", "dawn.com", "coursera.org", "mozilla.org",
         "reddit.com", "medium.com", "paypal.com", "netflix.com", "dropbox.com", "python.org"]
BRANDS = ["paypal", "microsoft", "apple", "amazon", "google", "netflix", "facebook", "dhl", "instagram", "binance"]
TLDS = ["top", "xyz", "click", "tk", "ml", "work", "icu", "support", "com", "net", "info"]
WORDS = ["login", "verify", "secure", "account", "update", "signin", "billing", "confirm", "wallet"]


def generate(path, n=1500, seed=42):
    r = random.Random(seed)
    rows = []
    for _ in range(n):
        d = r.choice(LEGIT)
        sub = r.choice(["www.", "docs.", "blog.", "", "support."])
        path_ = "/".join(r.choice(["a", "news", "docs", "post", "learn", "item", "2026", "help"]) + str(r.randint(0, 99)) for _ in range(r.randint(0, 3)))
        q = f"?id={r.randint(1, 9999)}&ref=home" if r.random() < .2 else ""
        scheme = "https" if r.random() < .96 else "http"
        rows.append((f"{scheme}://{sub}{d}/{path_}{q}", 0))
        b, w1, w2, t = r.choice(BRANDS), r.choice(WORDS), r.choice(WORDS), r.choice(TLDS)
        host = r.choice([
            f"{b}-{w1}.{t}", f"{w1}-{b}-{w2}.{t}", f"{b}.{w1}.{r.choice(['verify','secure','id'])}{r.randint(1,99)}.{t}",
            f"{r.randint(11, 223)}.{r.randint(0, 255)}.{r.randint(0, 255)}.{r.randint(1, 254)}",
            f"secure.{b}.com.{w1}-{r.randint(10, 99)}.{t}", f"{b}{r.randint(1, 99)}{w1}.com"])
        p2 = f"/{w1}/{w2}.php?id={r.randint(1000, 99999)}&session={r.randint(10**5, 10**6)}"
        if r.random() < .12:
            u = f"http://bit.ly/{r.choice(['3xYz', '2aBc', '4Qrs'])}{r.randint(10, 99)}"
        elif r.random() < .08:
            u = f"http://{d}@{host}/{w1}"
        else:
            u = f"{r.choice(['http', 'http', 'https'])}://{host}{p2}"
        rows.append((u, 1))
    r.shuffle(rows)
    pd.DataFrame(rows, columns=["url", "label"]).to_csv(path, index=False)
