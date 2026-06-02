import json
from urllib import request

from visaflow.config import OPENROUTER_API_KEY, OPENROUTER_BASE_URL, OPENROUTER_MODEL


def openrouter_available() -> bool:
    return bool(OPENROUTER_API_KEY)


def call_openrouter(prompt: str, system_prompt: str = "You are a helpful assistant.") -> str:
    if not OPENROUTER_API_KEY:
        raise RuntimeError("OPENROUTER_API_KEY is not set.")

    payload = {
        "model": OPENROUTER_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
    }

    data = json.dumps(payload).encode("utf-8")

    req = request.Request(
        f"{OPENROUTER_BASE_URL}/chat/completions",
        data=data,
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    with request.urlopen(req, timeout=60) as response:
        result = json.loads(response.read().decode("utf-8"))

    return result["choices"][0]["message"]["content"]
