from pathlib import Path


def test_app_contains_file_upload_mode():
    content = Path("app.py").read_text(encoding="utf-8")
    assert "Upload file" in content
    assert "file_uploader" in content
