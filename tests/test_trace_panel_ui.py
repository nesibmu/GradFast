from pathlib import Path


def test_app_contains_trace_panel():
    content = Path("app.py").read_text(encoding="utf-8")
    assert "Trace View" in content
    assert "Source to Output Mapping" in content
