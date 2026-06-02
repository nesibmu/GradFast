from pathlib import Path


def test_app_contains_new_robustness_presets():
    content = Path("app.py").read_text(encoding="utf-8")
    assert "Escalated admin case" in content
    assert "Weak noisy case" in content
    assert "graceful behavior on incomplete input" in content
