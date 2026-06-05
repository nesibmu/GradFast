from pathlib import Path


def test_demo_checklist_copy_cleanup_present():
    content = Path("app.py").read_text(encoding="utf-8")
    assert "Show the next best action and the overall system confidence." in content
    assert "Use comparison mode to contrast strong and weak cases." in content
