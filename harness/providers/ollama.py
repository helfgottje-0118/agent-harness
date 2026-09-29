"""Ollama chat provider with tool-calling support.

Talks to Ollama's /api/chat endpoint (non-streaming). The model must
support tools (e.g. qwen2.5, qwen3, llama3.1+, mistral-nemo).
"""
from __future__ import annotations

import json

import requests


class OllamaError(RuntimeError):
    pass


class OllamaProvider:
    def __init__(self, host: str, model: str, timeout: int = 300):
        self.host = host.rstrip("/")
        self.model = model
        self.timeout = timeout

    def check(self) -> None:
        """Raise OllamaError if the server or model isn't reachable."""
        try:
            r = requests.get(f"{self.host}/api/tags", timeout=10)
            r.raise_for_status()
        except requests.RequestException as e:
            raise OllamaError(
                f"Cannot reach Ollama at {self.host}. Is `ollama serve` running? ({e})"
            )
        models = [m.get("name", "") for m in r.json().get("models", [])]
        if not any(self.model == m or m.startswith(self.model + ":") or self.model.startswith(m) for m in models):
            raise OllamaError(
                f"Model '{self.model}' not found on {self.host}. "
                f"Available: {', '.join(models) or 'none'}. Pull one with `ollama pull {self.model}`."
            )

    def chat(self, messages: list[dict], tools: list[dict]) -> dict:
        """One chat turn. Returns the assistant message dict, which may
        contain 'content' and/or 'tool_calls' (OpenAI-style)."""
        payload = {
            "model": self.model,
            "messages": messages,
            "tools": tools,
            "stream": False,
            "options": {"temperature": 0.2},
        }
        try:
            r = requests.post(f"{self.host}/api/chat", json=payload, timeout=self.timeout)
            r.raise_for_status()
        except requests.RequestException as e:
            raise OllamaError(f"Ollama chat request failed: {e}")
        msg = r.json().get("message", {})
        # Normalize tool_calls: ensure arguments is a dict
        for tc in msg.get("tool_calls") or []:
            fn = tc.get("function", {})
            args = fn.get("arguments", {})
            if isinstance(args, str):
                try:
                    fn["arguments"] = json.loads(args) if args.strip() else {}
                except json.JSONDecodeError:
                    fn["arguments"] = {"_raw": args}
        return msg
