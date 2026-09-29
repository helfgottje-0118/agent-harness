"""Shell tool: run commands with timeouts and basic safety guardrails."""
from __future__ import annotations

import os
import subprocess

# Refuse commands matching these substrings — the agent should not need them.
_DENY = [
    "rm -rf /", "rm -rf ~", "rm -rf /*", "mkfs", ":(){:|:&};:",
    "dd if=", "dd of=/dev", "> /dev/sd", "chmod -R 777 /",
    "curl | sh", "wget | sh", "shutdown", "reboot", "poweroff",
]

_MAX_OUTPUT = 30000


def shell_exec(command: str, workdir: str, timeout: int = 60) -> str:
    lowered = command.lower()
    for bad in _DENY:
        if bad in lowered:
            return f"Refused: command contains blocked pattern '{bad}'."
    os.makedirs(workdir, exist_ok=True)
    try:
        proc = subprocess.run(
            command,
            shell=True,
            cwd=workdir,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as e:
        out = (e.stdout or "") + (e.stderr or "")
        return f"Timed out after {timeout}s.\nPartial output:\n{_truncate(out)}"
    except Exception as e:
        return f"Failed to run command: {e}"
    out = ""
    if proc.stdout:
        out += proc.stdout
    if proc.stderr:
        out += ("\n[stderr]\n" if out else "[stderr]\n") + proc.stderr
    out = _truncate(out.strip())
    return f"[exit {proc.returncode}]\n{out}" if out else f"[exit {proc.returncode}] (no output)"


def _truncate(text: str) -> str:
    if len(text) > _MAX_OUTPUT:
        return text[:_MAX_OUTPUT] + f"\n... [truncated, {len(text)} chars total]"
    return text
