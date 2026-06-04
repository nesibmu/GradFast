from pathlib import Path


def test_app_contains_task_digest_output():
    content = Path("app.py").read_text(encoding="utf-8")
    assert "Task Digest" in content
    assert "download_task_digest" in content
