from pathlib import Path


def test_final_ui_wording_cleanup_present():
    content = Path("app.py").read_text(encoding="utf-8")
    assert "Preset Notes" in content
    assert "Demo Comparison Guide" in content
