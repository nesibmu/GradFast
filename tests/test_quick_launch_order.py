from pathlib import Path


def test_quick_launch_order_is_curated():
    content = Path("app.py").read_text(encoding="utf-8")
    assert '"Mixed admin case"' in content
    assert '"Escalated admin case"' in content
    assert '"Weak noisy case"' in content
