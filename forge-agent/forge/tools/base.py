from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Any

@dataclass
class Tool:
    name: str
    description: str
    parameters: dict
    handler: Callable[..., Any]
    toolset: str

    def schema(self):
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            }
        }

class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool):
        self._tools[tool.name] = tool

    def names(self):
        return sorted(self._tools)

    def tools_for_sets(self, toolsets: list[str]):
        allowed = set(toolsets)
        return [t for t in self._tools.values() if t.toolset in allowed]

    def get(self, name: str):
        return self._tools.get(name)
