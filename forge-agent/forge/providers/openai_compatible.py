from __future__ import annotations
import httpx

class OpenAICompatibleProvider:
    def __init__(self, config):
        p = config["provider"]
        self.base_url = p["base_url"].rstrip("/")
        self.api_key = p.get("api_key", "")
        self.model = p["model"]

    def chat(self, messages, tools=None, model=None):
        headers = {"Content-Type":"application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        payload = {"model": model or self.model, "messages": messages}
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"
        r = httpx.post(f"{self.base_url}/chat/completions", headers=headers, json=payload, timeout=300)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]
