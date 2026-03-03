"""
llm_client.py - Single shared LLM client using OpenAI SDK.

Ollama exposes an OpenAI-compatible API at http://localhost:11434/v1,
so we use one client for everything. No raw requests.post() anywhere.
"""
import os
from openai import OpenAI

def get_client() -> OpenAI:
    """Return an OpenAI client pointed at local Ollama."""
    return OpenAI(
        base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1"),
        api_key="ollama",  # Ollama ignores this but the SDK requires it
    )

def chat(system: str, user: str, temperature: float = 0.3, model: str = None) -> str:
    """Simple synchronous chat call. Raises on connection failure."""
    client = get_client()
    model  = model or os.getenv("OLLAMA_MODEL", "llama3.2")
    resp = client.chat.completions.create(
        model=model,
        temperature=temperature,
        messages=[
            {"role": "system", "content": system},
            {"role": "user",   "content": user},
        ],
    )
    return resp.choices[0].message.content.strip()
