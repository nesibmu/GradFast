from pathlib import Path


def test_small_preset_note_cleanup_present():
    content = Path("app.py").read_text(encoding="utf-8")
    assert "stronger urgency signals" in content
    assert "Quick Launch Presets" in content
