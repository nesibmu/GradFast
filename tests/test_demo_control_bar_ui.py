from pathlib import Path


def test_app_contains_demo_control_bar():
    content = Path("app.py").read_text(encoding="utf-8")
    assert "Demo Control Bar" in content
    assert "Reset demo state" in content
    assert "Results are currently loaded and persistent." in content
