from pathlib import Path


def test_app_contains_draft_comparison():
    content = Path("app.py").read_text(encoding="utf-8")
    assert "Show baseline vs enhanced draft" in content
    assert "Baseline Draft" in content
    assert "Enhanced Draft" in content
