from pathlib import Path


def test_app_contains_title():
    content = Path("app.py").read_text(encoding="utf-8")
    assert "VisaFlow" in content
    assert "Input mode" in content
