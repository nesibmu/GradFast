from pathlib import Path


def test_app_contains_demo_script_panel():
    content = Path("app.py").read_text(encoding="utf-8")
    assert "Guided Demo Script" in content
    assert "Suggested presentation flow" in content
    assert "Show demo script panel" in content
