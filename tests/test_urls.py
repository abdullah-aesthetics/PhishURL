from phishurl.features import extract, reasons
from phishurl.model import load_model, score_url, train_and_save
from phishurl.sample import generate


def test_features_and_reasons():
    f = extract("http://192.168.1.5/login")
    assert f["has_ip"] == 1 and f["https"] == 0
    assert any("IP" in t for _, t in reasons(f))
    g = extract("https://www.github.com/org/repo")
    assert g["has_ip"] == 0 and g["https"] == 1 and reasons(g) == []
    assert extract("https://paypal.evil.xyz/x")["brand_mismatch"] == 1


def test_train_and_score(tmp_path):
    data = tmp_path / "u.csv"
    generate(data, n=300)
    m = train_and_save(data, tmp_path / "m")
    assert all(r["test"]["f1"] > 0.8 for r in m["models"].values())
    b = load_model(tmp_path / "m")
    bad = score_url("http://paypal-secure-login.top/verify/account.php?id=1&session=2", b)
    ok = score_url("https://www.github.com/org/repo", b)
    assert bad["risk"] > ok["risk"]
