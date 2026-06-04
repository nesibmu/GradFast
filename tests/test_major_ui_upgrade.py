from pathlib import Path


def test_app_contains_overview_and_confidence_ui():
    content = Path("app.py").read_text(encoding="utf-8")
    assert "Overview" in content
    assert "confidence:" in content
    assert "Operational Summary" in content
    assert "Task Plan" in content
