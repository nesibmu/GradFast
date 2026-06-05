from pathlib import Path


def test_app_contains_extraction_dashboard():
    content = Path("app.py").read_text(encoding="utf-8")
    assert "Extraction Dashboard" in content
    assert "Evidence by Category" in content
    assert "render_compact_findings" in content
