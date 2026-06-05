from visaflow.llm.openrouter_client import openrouter_available


def test_openrouter_available_returns_bool():
    assert isinstance(openrouter_available(), bool)
