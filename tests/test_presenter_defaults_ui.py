from pathlib import Path


def test_app_contains_presenter_defaults():
    content = Path("app.py").read_text(encoding="utf-8")
    assert 'DEFAULT_PRESET = "Mixed admin case"' in content
    assert "Recommended first run: **Mixed admin case**" in content
    assert "Suggested preset: Mixed admin case" in content
