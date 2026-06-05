from pathlib import Path


def test_output_tab_order_is_demo_friendly():
    content = Path("app.py").read_text(encoding="utf-8")
    assert '["Short Summary", "Email-Ready Reply", "Task Digest"' in content
