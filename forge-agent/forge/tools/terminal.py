from __future__ import annotations
import subprocess
from pathlib import Path
from .base import Tool

def build_terminal_tool(config):
    def terminal(command: str, cwd: str | None = None, timeout: int | None = None):
        base = Path(cwd or config["terminal"].get("cwd", ".")).expanduser().resolve()
        if not base.exists():
            return {"ok": False, "error": f"directory does not exist: {base}"}
        try:
            p = subprocess.run(command, cwd=str(base), shell=True, text=True, capture_output=True,
                               timeout=timeout or config["terminal"].get("timeout", 180))
            return {"ok": p.returncode == 0, "returncode": p.returncode,
                    "stdout": p.stdout, "stderr": p.stderr, "cwd": str(base)}
        except subprocess.TimeoutExpired as e:
            return {"ok": False, "error": "command timed out", "stdout": e.stdout, "stderr": e.stderr}

    return Tool(
        name="terminal",
        description="Execute a shell command on the configured machine.",
        toolset="terminal",
        parameters={
            "type": "object",
            "properties": {
                "command": {"type": "string"},
                "cwd": {"type": ["string", "null"]},
                "timeout": {"type": ["integer", "null"]},
            },
            "required": ["command"],
            "additionalProperties": False,
        },
        handler=terminal,
    )
