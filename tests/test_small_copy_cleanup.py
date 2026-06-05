from pathlib import Path


def test_small_copy_cleanup_present():
    content = Path("app.py").read_text(encoding="utf-8")
    assert "heavier multi-deadline handling" in content
    assert "multiple deadlines, document requests, and follow-up actions" in content
