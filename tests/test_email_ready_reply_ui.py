from pathlib import Path


def test_app_contains_email_ready_reply():
    content = Path("app.py").read_text(encoding="utf-8")
    assert "Email-Ready Reply" in content
    assert "download_email_reply" in content
