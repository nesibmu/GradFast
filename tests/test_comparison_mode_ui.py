from pathlib import Path


def test_app_contains_comparison_mode():
    content = Path("app.py").read_text(encoding="utf-8")
    assert "Comparison mode" in content
    assert "Preset Comparison" in content
    assert "render_comparison_column" in content
