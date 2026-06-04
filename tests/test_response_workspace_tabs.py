from pathlib import Path


def test_app_contains_response_workspace_tabs():
    content = Path("app.py").read_text(encoding="utf-8")
    assert "Response Workspace" in content
    assert '"Summary", "Baseline Draft", "Enhanced Draft", "Checklist"' in content
