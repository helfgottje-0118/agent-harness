"""File tools, sandboxed to a workspace root.

Every path is resolved against the workspace and rejected if it escapes it.
"""
from __future__ import annotations

import os

_MAX_READ = 100000


def _resolve(workspace: str, relpath: str) -> str:
    root = os.path.realpath(workspace)
    target = os.path.realpath(os.path.join(root, relpath))
    if target != root and not target.startswith(root + os.sep):
        raise ValueError(f"Path '{relpath}' escapes the workspace.")
    return target


def file_read(workspace: str, path: str, max_chars: int = 20000) -> str:
    target = _resolve(workspace, path)
    if not os.path.isfile(target):
        return f"Error: '{path}' does not exist or is not a file."
    try:
        with open(target, "r", encoding="utf-8", errors="replace") as f:
            content = f.read(min(max_chars, _MAX_READ) + 1)
    except OSError as e:
        return f"Error reading '{path}': {e}"
    if len(content) > max_chars:
        return content[:max_chars] + f"\n... [truncated at {max_chars} chars]"
    return content


def file_write(workspace: str, path: str, content: str) -> str:
    target = _resolve(workspace, path)
    try:
        os.makedirs(os.path.dirname(target) or workspace, exist_ok=True)
        with open(target, "w", encoding="utf-8") as f:
            f.write(content)
    except OSError as e:
        return f"Error writing '{path}': {e}"
    return f"Wrote {len(content)} chars to '{path}'."


def file_edit(workspace: str, path: str, old_text: str, new_text: str) -> str:
    target = _resolve(workspace, path)
    if not os.path.isfile(target):
        return f"Error: '{path}' does not exist."
    try:
        with open(target, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
    except OSError as e:
        return f"Error reading '{path}': {e}"
    if old_text not in content:
        return f"Error: old_text not found in '{path}'."
    content = content.replace(old_text, new_text, 1)
    try:
        with open(target, "w", encoding="utf-8") as f:
            f.write(content)
    except OSError as e:
        return f"Error writing '{path}': {e}"
    return f"Edited '{path}' (replaced first occurrence)."


def file_list(workspace: str, path: str = ".") -> str:
    target = _resolve(workspace, path)
    if not os.path.isdir(target):
        return f"Error: '{path}' is not a directory."
    try:
        entries = sorted(os.listdir(target))
    except OSError as e:
        return f"Error listing '{path}': {e}"
    lines = []
    for e in entries:
        full = os.path.join(target, e)
        lines.append(f"{e}/" if os.path.isdir(full) else e)
    return "\n".join(lines) if lines else "(empty directory)"
