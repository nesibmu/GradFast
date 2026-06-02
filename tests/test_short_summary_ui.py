from pathlib import Path


def test_app_contains_short_summary_output():
    content = Path("app.py").read_text(encoding="utf-8")
    assert "Short Summary" in content
    assert "download_short_summary" in content
