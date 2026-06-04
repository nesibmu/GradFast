from pathlib import Path


def test_app_contains_session_state_and_quick_launch():
    content = Path("app.py").read_text(encoding="utf-8")
    assert "st.session_state.results" in content
    assert "Quick Demo Launch" in content
    assert "Clear current results" in content
