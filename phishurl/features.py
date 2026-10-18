"""Lexical URL features + human-readable reasons (no network access needed)."""
import math
import re
from urllib.parse import urlparse

SHORT = {"bit.ly", "tinyurl.com", "t.co", "goo.gl", "ow.ly", "is.gd", "cutt.ly", "rebrand.ly"}
BAD_TLD = {"zip", "top", "xyz", "click", "tk", "ml", "ga", "cf", "gq", "work", "support", "icu", "buzz", "loan"}
WORDS = ["login", "signin", "verify", "secure", "account", "update", "confirm", "password",
         "bank", "wallet", "billing", "suspend", "unlock", "free", "prize", "invoice"]
BRANDS = {"paypal": "paypal.com", "microsoft": "microsoft.com", "apple": "apple.com", "amazon": "amazon.com",
          "google": "google.com", "netflix": "netflix.com", "facebook": "facebook.com", "dhl": "dhl.com",
          "instagram": "instagram.com", "binance": "binance.com"}
FEATURES = ["url_len", "host_len", "path_len", "query_len", "dots", "host_hyphens", "digits", "digit_ratio",
            "subdomains", "has_ip", "has_at", "https", "has_port", "bad_tld", "shortener", "susp_words",
            "brand_mismatch", "host_entropy", "punycode", "path_depth", "special"]
URL_RE = re.compile(r"(?:https?://|www\.)[^\s<>\"')\]]+", re.I)


def _entropy(s):
    if not s:
        return 0.0
    return -sum(s.count(c) / len(s) * math.log2(s.count(c) / len(s)) for c in set(s))


def extract(url: str) -> dict:
    u = url.strip()
    p = urlparse(u if "//" in u else "http://" + u)
    host, path, q = (p.hostname or "").lower(), p.path or "", p.query or ""
    labels = host.split(".") if host else []
    try:
        port = p.port
    except ValueError:
        port = -1
    low = u.lower()
    brand = any(b in host and not (host == d or host.endswith("." + d)) for b, d in BRANDS.items())
    return {"url_len": len(u), "host_len": len(host), "path_len": len(path), "query_len": len(q),
            "dots": host.count("."), "host_hyphens": host.count("-"), "digits": sum(c.isdigit() for c in u),
            "digit_ratio": round(sum(c.isdigit() for c in u) / max(len(u), 1), 3),
            "subdomains": max(0, len(labels) - 2), "has_ip": int(bool(re.fullmatch(r"\d{1,3}(\.\d{1,3}){3}", host))),
            "has_at": int("@" in u), "https": int(low.startswith("https://")),
            "has_port": int(port not in (None, 80, 443)), "bad_tld": int(bool(labels) and labels[-1] in BAD_TLD),
            "shortener": int(host in SHORT), "susp_words": sum(w in low for w in WORDS),
            "brand_mismatch": int(brand), "host_entropy": round(_entropy(host), 3),
            "punycode": int("xn--" in host), "path_depth": path.count("/"), "special": sum(u.count(c) for c in "?=&%_~")}


def reasons(f: dict) -> list:
    """Plain-English warnings derived from the features (explainability)."""
    r = []
    if f["has_ip"]: r.append(("high", "Uses a raw IP address instead of a domain name"))
    if f["brand_mismatch"]: r.append(("high", "Mentions a well-known brand but is not that brand's real domain"))
    if f["has_at"]: r.append(("high", "Contains '@', which can hide the real destination"))
    if f["punycode"]: r.append(("high", "Uses punycode (possible look-alike characters)"))
    if f["shortener"]: r.append(("medium", "URL shortener hides the real destination"))
    if f["bad_tld"]: r.append(("medium", "High-abuse top-level domain"))
    if not f["https"]: r.append(("medium", "Does not use HTTPS"))
    if f["susp_words"] >= 2: r.append(("medium", f"Contains {f['susp_words']} sensitive words (login, verify, secure ...)"))
    if f["subdomains"] >= 3: r.append(("medium", "Unusually many subdomains"))
    if f["host_hyphens"] >= 2: r.append(("low", "Many hyphens in the domain"))
    if f["has_port"]: r.append(("low", "Uses a non-standard port"))
    if f["url_len"] > 75: r.append(("low", "Very long URL"))
    return r
