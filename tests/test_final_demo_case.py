from pathlib import Path


def test_final_demo_case_exists():
    content = Path("app.py").read_text(encoding="utf-8")
    assert "Mixed admin case" in content

    sample = Path("data/samples/mixed_admin_case.txt").read_text(encoding="utf-8")
    assert "housing agreement" in sample
    assert "passport" in sample
