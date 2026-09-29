"""Tool registry and built-in tools: shell, files, web."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass
class Tool:
    name: str
    description: str
    parameters: dict  # JSON Schema for arguments
    func: Callable[..., str]

    def to_ollama(self) -> dict:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }


class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        self._tools[tool.name] = tool

    def names(self) -> list[str]:
        return list(self._tools.keys())

    def to_ollama(self) -> list[dict]:
        return [t.to_ollama() for t in self._tools.values()]

    def execute(self, name: str, arguments: dict[str, Any]) -> str:
        tool = self._tools.get(name)
        if tool is None:
            return f"Error: unknown tool '{name}'. Available: {', '.join(self.names())}"
        try:
            result = tool.func(**arguments)
        except TypeError as e:
            return f"Error: bad arguments for '{name}': {e}"
        except Exception as e:  # tools should not crash the loop
            return f"Error executing '{name}': {e}"
        return str(result) if result is not None else ""


def _str_prop(desc: str) -> dict:
    return {"type": "string", "description": desc}


def build_default_registry(workspace: str, tool_timeout: int = 60) -> ToolRegistry:
    """Assemble the standard toolset: shell, file ops (sandboxed), web."""
    from . import shell as _shell
    from . import files as _files
    from . import web as _web

    reg = ToolRegistry()

    reg.register(Tool(
        name="shell_exec",
        description=(
            "Run a shell command and return its output. Working directory is the "
            "agent workspace. Long-running or interactive commands are not supported; "
            "use timeouts inside the command itself for slow operations."
        ),
        parameters={
            "type": "object",
            "properties": {
                "command": _str_prop("The shell command to run."),
                "timeout": {"type": "integer", "description": "Timeout in seconds (default 60, max 600)."},
            },
            "required": ["command"],
        },
        func=lambda command, timeout=60: _shell.shell_exec(command, workspace, min(timeout, 600)),
    ))

    reg.register(Tool(
        name="file_read",
        description="Read a text file from the workspace. Paths are relative to the workspace root.",
        parameters={
            "type": "object",
            "properties": {
                "path": _str_prop("Relative path of the file to read."),
                "max_chars": {"type": "integer", "description": "Max characters to return (default 20000)."},
            },
            "required": ["path"],
        },
        func=lambda path, max_chars=20000: _files.file_read(workspace, path, max_chars),
    ))

    reg.register(Tool(
        name="file_write",
        description="Write (create or overwrite) a text file in the workspace. Parent dirs are created.",
        parameters={
            "type": "object",
            "properties": {
                "path": _str_prop("Relative path of the file to write."),
                "content": _str_prop("Full content to write."),
            },
            "required": ["path", "content"],
        },
        func=lambda path, content: _files.file_write(workspace, path, content),
    ))

    reg.register(Tool(
        name="file_edit",
        description="Replace the first occurrence of old_text with new_text in a workspace file.",
        parameters={
            "type": "object",
            "properties": {
                "path": _str_prop("Relative path of the file to edit."),
                "old_text": _str_prop("Exact text to find (first occurrence is replaced)."),
                "new_text": _str_prop("Replacement text."),
            },
            "required": ["path", "old_text", "new_text"],
        },
        func=lambda path, old_text, new_text: _files.file_edit(workspace, path, old_text, new_text),
    ))

    reg.register(Tool(
        name="file_list",
        description="List files and directories under a workspace path.",
        parameters={
            "type": "object",
            "properties": {
                "path": _str_prop("Relative directory to list (default '.')."),
            },
        },
        func=lambda path=".": _files.file_list(workspace, path),
    ))

    reg.register(Tool(
        name="web_fetch",
        description="Fetch a URL and return its readable text content (HTML stripped).",
        parameters={
            "type": "object",
            "properties": {
                "url": _str_prop("The http(s) URL to fetch."),
                "max_chars": {"type": "integer", "description": "Max characters to return (default 15000)."},
            },
            "required": ["url"],
        },
        func=lambda url, max_chars=15000: _web.web_fetch(url, max_chars),
    ))

    reg.register(Tool(
        name="web_search",
        description="Search the web and return titles, URLs and snippets for the query.",
        parameters={
            "type": "object",
            "properties": {
                "query": _str_prop("The search query."),
                "num_results": {"type": "integer", "description": "How many results (default 5, max 10)."},
            },
            "required": ["query"],
        },
        func=lambda query, num_results=5: _web.web_search(query, min(num_results, 10)),
    ))

    return reg


def dump_result_preview(text: str, limit: int = 2000) -> str:
    text = str(text)
    return text if len(text) <= limit else text[:limit] + f"\n... [truncated, {len(text)} chars total]"
