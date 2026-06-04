from pathlib import Path


def test_app_contains_editable_draft_features():
    content = Path("app.py").read_text(encoding="utf-8")
    assert "Editable draft" in content
    assert "download_button" in content
