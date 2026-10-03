from __future__ import annotations
from pathlib import Path
from .base import Tool

def read_file(path: str):
    p = Path(path).expanduser()
    return {"ok": True, "path": str(p), "content": p.read_text()}

def write_file(path: str, content: str, create_parents: bool = True):
    p = Path(path).expanduser()
    if create_parents:
        p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content)
    return {"ok": True, "path": str(p), "bytes": len(content.encode())}

def patch_file(path: str, old: str, new: str):
    p = Path(path).expanduser()
    text = p.read_text()
    if old not in text:
        return {"ok": False, "error": "old text not found", "path": str(p)}
    p.write_text(text.replace(old, new, 1))
    return {"ok": True, "path": str(p)}

def tools():
    return [
        Tool("read_file", "Read a UTF-8 text file.", {
            "type":"object","properties":{"path":{"type":"string"}},
            "required":["path"],"additionalProperties":False
        }, read_file, "file"),
        Tool("write_file", "Write a UTF-8 text file.", {
            "type":"object","properties":{
                "path":{"type":"string"},"content":{"type":"string"},
                "create_parents":{"type":"boolean"}},
            "required":["path","content"],"additionalProperties":False
        }, write_file, "file"),
        Tool("patch", "Replace the first exact occurrence of text in a UTF-8 file.", {
            "type":"object","properties":{
                "path":{"type":"string"},"old":{"type":"string"},"new":{"type":"string"}},
            "required":["path","old","new"],"additionalProperties":False
        }, patch_file, "file")
    ]
