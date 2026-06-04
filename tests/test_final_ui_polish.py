from pathlib import Path


def test_app_contains_polished_labels():
    content = Path("app.py").read_text(encoding="utf-8")
    assert "Source Text" in content
    assert "Evidence Snippets" in content
    assert "Choose a preset, sample file, pasted text, or uploaded file" in content
