from pathlib import Path


def test_app_contains_comparison_summary():
    content = Path("app.py").read_text(encoding="utf-8")
    assert "Comparison Summary" in content
    assert "render_comparison_summary" in content
