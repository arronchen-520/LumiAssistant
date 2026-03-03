"""
llm_client.py — 多 LLM 提供商支持
Supports: Ollama (local) · Groq · OpenAI · any OpenAI-compatible endpoint

Configure via .env:
    LLM_PROVIDER = ollama | groq | openai | custom
    LLM_MODEL    = llama3.2 | llama-3.1-70b-versatile | gpt-4o-mini | …
    LLM_BASE_URL = http://localhost:11434/v1   (auto-set for known providers)
    LLM_API_KEY  = your_key_here              (not needed for Ollama)
"""
import os
from openai import OpenAI

_client: OpenAI | None = None
_active_provider: str = ""


def _build_client() -> tuple[OpenAI, str]:
    provider = os.getenv("LLM_PROVIDER", "ollama").lower().strip()

    if provider == "groq":
        base_url = "https://api.groq.com/openai/v1"
        api_key  = os.getenv("LLM_API_KEY") or os.getenv("GROQ_API_KEY", "")
        model    = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")
    elif provider == "openai":
        base_url = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1")
        api_key  = os.getenv("LLM_API_KEY", "")
        model    = os.getenv("LLM_MODEL", "gpt-4o-mini")
    elif provider == "custom":
        base_url = os.getenv("LLM_BASE_URL", "http://localhost:11434/v1")
        api_key  = os.getenv("LLM_API_KEY", "custom")
        model    = os.getenv("LLM_MODEL", "llama3.2")
    else:  # ollama (default)
        base_url = os.getenv("LLM_BASE_URL", "http://localhost:11434/v1")
        api_key  = os.getenv("LLM_API_KEY", "ollama")
        model    = os.getenv("LLM_MODEL") or os.getenv("OLLAMA_MODEL", "llama3.2")

    return OpenAI(base_url=base_url, api_key=api_key), model


def get_client() -> OpenAI:
    """Singleton client — built once, reused across all calls."""
    global _client, _active_provider
    if _client is None:
        _client, _ = _build_client()
        _active_provider = os.getenv("LLM_PROVIDER", "ollama").lower()
    return _client


def get_model() -> str:
    """Returns the configured model name."""
    _, model = _build_client()
    return model


def get_provider_info() -> dict:
    """Used by main.py for the startup banner."""
    provider = os.getenv("LLM_PROVIDER", "ollama").lower()
    _, model = _build_client()
    urls = {
        "groq":   "api.groq.com",
        "openai": "api.openai.com",
        "custom": os.getenv("LLM_BASE_URL", "custom"),
        "ollama": os.getenv("LLM_BASE_URL", "localhost:11434"),
    }
    return {"provider": provider, "model": model, "url": urls.get(provider, "?")}


def chat(
    system: str,
    user: str,
    temperature: float = 0.3,
    model: str | None = None,
    history: list[dict] | None = None,
) -> str:
    """
    Synchronous chat. All LLM calls in the app funnel through here.

    Args:
        system:      System prompt.
        user:        Latest user message.
        temperature: Sampling temperature.
        model:       Override model (defaults to LLM_MODEL / provider default).
        history:     Prior turns [{role, content}] inserted before user message.
    """
    client = get_client()
    model  = model or get_model()

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
