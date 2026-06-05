from pathlib import Path


def test_app_contains_intro_text():
    content = Path("app.py").read_text(encoding="utf-8")
    assert "VisaFlow helps turn messy administrative emails" in content
    assert "structured extracted information" in content
