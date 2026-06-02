from pathlib import Path


def test_app_contains_ops_handoff():
    content = Path("app.py").read_text(encoding="utf-8")
    assert "Ops Handoff" in content
    assert "download_ops_handoff" in content
