from pathlib import Path


def test_app_contains_preset_notes():
    content = Path("app.py").read_text(encoding="utf-8")
    assert "Preset Notes" in content
    assert "Selected preset" in content
    assert "Best default demo." in content
