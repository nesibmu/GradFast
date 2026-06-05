from pathlib import Path


def test_app_contains_metrics_and_sections():
    content = Path("app.py").read_text(encoding="utf-8")
    assert "Planned Tasks" in content
    assert "Next-Step Summary" in content
    assert "metric(" in content
