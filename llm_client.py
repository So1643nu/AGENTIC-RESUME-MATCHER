"""
llm_client.py
Thin wrapper around a locally running Ollama model (no API key required).

If Ollama is not installed or not running, `is_available()` returns False
and the calling agent (SuggestionAgent) will automatically fall back to a
rule-based response instead of failing. This keeps the whole app working
even on a machine with no local LLM set up.

To enable real LLM-generated suggestions:
    1. Install Ollama from https://ollama.com
    2. Run:  ollama pull llama3.2
    3. Ollama runs a local server automatically at http://localhost:11434
"""

import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
DEFAULT_MODEL = "llama3.2"


def is_available() -> bool:
    """Quick check whether a local Ollama server is reachable."""
    try:
        resp = requests.get("http://localhost:11434", timeout=1.5)
        return resp.status_code == 200
    except Exception:
        return False


def generate(prompt: str, model: str = DEFAULT_MODEL, timeout: int = 30) -> str:
    """
    Send a prompt to the local Ollama model and return the text response.
    Raises an exception on failure -- callers should catch it and fall back.
    """
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }
    response = requests.post(OLLAMA_URL, json=payload, timeout=timeout)
    response.raise_for_status()
    data = response.json()
    return data.get("response", "").strip()
