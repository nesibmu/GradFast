from pathlib import Path


def test_app_contains_minimal_view():
    content = Path("app.py").read_text(encoding="utf-8")
    assert "Minimal view" in content
    assert "download_ops_handoff_minimal" in content
    assert "download_enhanced_minimal" in content
