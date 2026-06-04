from pathlib import Path


def test_app_contains_failure_and_empty_state_handling():
    content = Path("app.py").read_text(encoding="utf-8")
    assert "Only a small amount of structured information was found" in content
    assert "No task plan could be generated from this input yet." in content
    assert "This case produced very little structured signal." in content
