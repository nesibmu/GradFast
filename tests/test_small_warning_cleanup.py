from pathlib import Path


def test_small_warning_cleanup_present():
    content = Path("app.py").read_text(encoding="utf-8")
    assert "Only limited structured information was found. Results may be incomplete." in content
    assert "No task plan was generated from this input." in content
