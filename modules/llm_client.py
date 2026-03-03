"""
llm_client.py - Single shared LLM client using OpenAI SDK.

Ollama exposes an OpenAI-compatible API at http://localhost:11434/v1,
so we use one client for everything. No raw requests.post() anywhere.

Singleton pattern: client is created once and reused across all calls.
"""
import os
from openai import OpenAI

_client: OpenAI | None = None


def get_client() -> OpenAI:
    """Return a singleton OpenAI client pointed at local Ollama."""
    global _client
    if _client is None:
        _client = OpenAI(
            base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1"),
            api_key="ollama",  # Ollama ignores this but the SDK requires it
        )
    return _client


def chat(
    system: str,
    user: str,
    temperature: float = 0.3,
    model: str = None,
    history: list[dict] | None = None,
) -> str:
    """
    Synchronous chat call. Supports optional multi-turn history.

    Args:
        system:      System prompt.
        user:        Latest user message.
        temperature: LLM temperature.
        model:       Override model name (defaults to OLLAMA_MODEL env var).
        history:     Optional list of prior {"role": ..., "content": ...} dicts
                     inserted *before* the current user message. Use this to
                     pass conversation history for stateful chat.

    Raises on connection failure.
    """
    client = get_client()
    model = model or os.getenv("OLLAMA_MODEL", "llama3.2")

    messages = [{"role": "system", "content": system}]
    if history:
        messages.extend(history)
    messages.append({"role": "user", "content": user})

    resp = client.chat.completions.create(
        model=model,
        temperature=temperature,
        messages=messages,
    )
    return resp.choices[0].message.content.strip()
