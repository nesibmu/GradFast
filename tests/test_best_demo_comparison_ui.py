from pathlib import Path


def test_app_contains_best_demo_comparison():
    content = Path("app.py").read_text(encoding="utf-8")
    assert "Best Demo Comparison" in content
    assert "Recommended comparison pair" in content
    assert "Mixed admin case" in content
    assert "Weak noisy case" in content
