from pathlib import Path


def test_app_contains_cleaner_ui_wording():
    content = Path("app.py").read_text(encoding="utf-8")
    assert "Extraction Overview" in content
    assert "Comparison Highlights" in content
    assert "Current results are loaded." in content
    assert "Outputs" in content
