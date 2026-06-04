from pathlib import Path


def test_app_contains_task_filters():
    content = Path("app.py").read_text(encoding="utf-8")
    assert "Filter by workflow" in content
    assert "Filter by priority" in content
