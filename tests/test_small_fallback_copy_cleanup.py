from pathlib import Path


def test_small_fallback_copy_cleanup_present():
    content = Path("app.py").read_text(encoding="utf-8")
    assert "generic follow-up rather than a detailed administrative request" in content
    assert "fallback behavior on incomplete input" in content
