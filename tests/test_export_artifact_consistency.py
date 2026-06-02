from pathlib import Path


def test_export_artifact_labels_and_filenames_are_consistent():
    content = Path("app.py").read_text(encoding="utf-8")
    assert "Export short summary" in content
    assert "Export task digest" in content
    assert "visaflow_short_summary_export.txt" in content
    assert "visaflow_operations_handoff_export.txt" in content
