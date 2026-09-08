"""
Thin wrapper around the Anthropic API. Kept in one file so there's exactly
one place that knows about API keys, model names, and retry/error handling.
"""

import os
from anthropic import Anthropic, APIError, APIConnectionError

MODEL = "claude-sonnet-4-5-20250929"


class LLMUnavailable(Exception):
    """Raised when the LLM step can't run (missing key, network, API error)."""


def get_client() -> Anthropic:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise LLMUnavailable(
            "ANTHROPIC_API_KEY is not set. Add it to your .env file or "
            "environment before running the app."
        )
    return Anthropic(api_key=api_key)


def call_llm(system: str, user: str, max_tokens: int = 1024) -> str:
    """Single-purpose call: system+user in, text out. Raises LLMUnavailable
    on any failure so callers can decide how to degrade gracefully."""
    try:
        client = get_client()
        resp = client.messages.create(
            model=MODEL,
            max_tokens=max_tokens,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        return "".join(
            block.text for block in resp.content if block.type == "text"
        ).strip()
    except LLMUnavailable:
        raise
    except (APIError, APIConnectionError) as e:
        raise LLMUnavailable(f"LLM call failed: {e}") from e
