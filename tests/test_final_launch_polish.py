from pathlib import Path


def test_final_launch_polish_present():
    content = Path("README.md").read_text(encoding="utf-8")
    assert "It is not intended to be a deployed production system." in content
