from pathlib import Path


def test_task_digest_copy_cleanup_present():
    content = Path("visaflow/drafting/drafter.py").read_text(encoding="utf-8")
    assert "Immediate focus items" in content
    assert "Blocked items" in content
