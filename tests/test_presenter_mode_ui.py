from pathlib import Path


def test_app_contains_presenter_mode():
    content = Path("app.py").read_text(encoding="utf-8")
    assert "Presenter mode" in content
    assert "download_enhanced_presenter" in content
