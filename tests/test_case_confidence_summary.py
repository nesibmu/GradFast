from pathlib import Path


def test_app_contains_case_confidence_summary():
    content = Path("app.py").read_text(encoding="utf-8")
    assert "System confidence" in content
    assert "compute_case_confidence" in content
