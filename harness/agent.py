"""The agent loop: a ReAct-style cycle of model -> tool calls -> model ..."""
from __future__ import annotations

import json

from .config import Config
from .providers import OllamaProvider
from .tools import ToolRegistry, build_default_registry, dump_result_preview

SYSTEM_PROMPT = """You are a capable autonomous agent running inside a tool harness.
You have tools for running shell commands, reading/writing/editing files in your
workspace, and accessing the web (fetch pages, search).

Rules:
- Work step by step. Use tools to gather facts instead of guessing.
- The shell runs in your workspace directory; file paths are relative to it.
- Prefer file tools over shell for reading/writing files.
- When a task is complete, give a concise summary of what you did and the outcome.
- If you are stuck after several attempts, explain what you tried and stop.
- Never attempt destructive system operations; stay within the workspace.
"""


class Agent:
    def __init__(self, config: Config, registry: ToolRegistry | None = None):
        self.config = config
        self.provider = OllamaProvider(config.host, config.model)
        self.registry = registry or build_default_registry(config.workspace, config.tool_timeout)

    def run(self, task: str, on_event=None) -> str:
        """Run the agent loop on a task. Returns the final answer.

        on_event(kind, data) is called with 'assistant', 'tool_call',
        'tool_result' events for UIs that want a live feed.
        """
        self.provider.check()
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": task},
        ]
        tools = self.registry.to_ollama()

        for i in range(self.config.max_iterations):
            msg = self.provider.chat(messages, tools)
            messages.append({k: v for k, v in msg.items() if k in ("role", "content", "tool_calls")})
            content = msg.get("content") or ""
            tool_calls = msg.get("tool_calls") or []

            if self.config.verbose or on_event:
                self._emit(on_event, "assistant", {"content": content, "n_tool_calls": len(tool_calls)})

            if not tool_calls:
                return content.strip() or "(model returned no content)"

            for tc in tool_calls:
                fn = tc.get("function", {})
                name = fn.get("name", "")
                args = fn.get("arguments", {}) or {}
                self._emit(on_event, "tool_call", {"name": name, "arguments": args})
                result = self.registry.execute(name, args)
                self._emit(on_event, "tool_result", {"name": name, "result": dump_result_preview(result)})
                messages.append({"role": "tool", "content": result})

        return (
            "(stopped: max iterations reached)\n\n"
            + (messages[-1].get("content") or "") if messages else ""
        )

    @staticmethod
    def _emit(on_event, kind, data):
        if on_event:
            try:
                on_event(kind, data)
            except Exception:
                pass
