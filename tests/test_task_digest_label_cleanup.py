from pathlib import Path


def test_task_digest_label_cleanup_present():
    content = Path("visaflow/drafting/drafter.py").read_text(encoding="utf-8")
    assert "Immediate focus" in content
    assert "Blocked tasks" in content
