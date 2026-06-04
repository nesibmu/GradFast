from visaflow.llm.openrouter_client import call_openrouter, openrouter_available


def maybe_call_llm(prompt: str, system_prompt: str = "You are a helpful assistant."):
    if not openrouter_available():
        return None
    return call_openrouter(prompt=prompt, system_prompt=system_prompt)
