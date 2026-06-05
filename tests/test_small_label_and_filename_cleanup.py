from pathlib import Path


def test_small_label_and_filename_cleanup_present():
    content = Path("app.py").read_text(encoding="utf-8")
    assert "Preset Notes and Usage" in content
    assert "visaflow_operations_handoff.txt" in content
