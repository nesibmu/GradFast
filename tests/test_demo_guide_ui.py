from pathlib import Path


def test_app_contains_demo_guide():
    content = Path("app.py").read_text(encoding="utf-8")
    assert "Demo guide" in content
    assert "Preset guide:" in content
    assert "Shows deadline extraction" in content
