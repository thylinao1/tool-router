"""LLM clients. The LLM is only ever asked to answer; it never chooses a tool."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request

SYSTEM_PROMPT = "You are a concise assistant. Answer in at most four sentences."


class OllamaLLM:
    name = "ollama"

    def __init__(self, model: str = "llama3.2:3b", host: str | None = None,
                 max_tokens: int = 160, timeout: int = 120) -> None:
        self.model = model
        host = (host or os.environ.get("OLLAMA_HOST", "http://localhost:11434")).rstrip("/")
        self.host = host if "://" in host else f"http://{host}"   # Ollama's own convention is host:port
        self.max_tokens = max_tokens
        self.timeout = timeout

    def is_available(self) -> bool:
        try:
            with urllib.request.urlopen(f"{self.host}/api/tags", timeout=2) as resp:
                models = [m["name"] for m in json.loads(resp.read()).get("models", [])]
            return self.model in models
        except (urllib.error.URLError, OSError, ValueError):
            return False

    def generate(self, prompt: str, system: str = SYSTEM_PROMPT) -> str:
        payload = json.dumps({
            "model": self.model,
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": prompt}],
            "stream": False,
            "options": {"num_predict": self.max_tokens, "temperature": 0.2},
        }).encode()
        req = urllib.request.Request(f"{self.host}/api/chat", data=payload,
                                     headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                return json.loads(resp.read())["message"]["content"].strip()
        except (urllib.error.URLError, OSError, KeyError, ValueError) as exc:
            return f"[llm unavailable: {exc}]"


class MockLLM:
    """Deterministic stand-in so the evaluation runs without a model server."""
    name = "mock"

    def is_available(self) -> bool:
        return True

    def generate(self, prompt: str, system: str = SYSTEM_PROMPT) -> str:
        return f"[mock LLM answer to: {prompt[:60]}]"


def get_llm(prefer: str = "ollama"):
    if prefer == "ollama":
        llm = OllamaLLM()
        if llm.is_available():
            return llm
    return MockLLM()
