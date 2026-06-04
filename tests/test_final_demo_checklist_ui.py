from pathlib import Path


def test_app_contains_final_demo_checklist():
    content = Path("app.py").read_text(encoding="utf-8")
    assert "Final Demo Checklist" in content
    assert "Recommended recording flow" in content
    assert "Open Mixed admin case first." in content
