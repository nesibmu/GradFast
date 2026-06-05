from pathlib import Path


def test_app_contains_hero_and_demo_state():
    content = Path("app.py").read_text(encoding="utf-8")
    assert "Current demo state" in content
    assert "AI operations agent for international-student bureaucracy" in content
