from pathlib import Path


def test_small_summary_confidence_cleanup_present():
    content = Path("app.py").read_text(encoding="utf-8")
    assert "earliest deadline should be handled first" in content
    assert "Overall system confidence" in content
