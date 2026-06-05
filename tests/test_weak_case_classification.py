from pathlib import Path


def test_app_contains_weak_case_classification():
    content = Path("app.py").read_text(encoding="utf-8")
    assert "classify_weak_case" in content
    assert "generic follow-up message" in content
    assert "soft reminder message" in content
