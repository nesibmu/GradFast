from pathlib import Path


def test_app_contains_demo_presets():
    content = Path("app.py").read_text(encoding="utf-8")
    assert "Demo preset" in content
    assert "Housing follow-up" in content
    assert "Financial aid review" in content
