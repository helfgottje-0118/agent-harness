from __future__ import annotations
import sqlite3, time
from .base import Tool
from forge.config import CONFIG_DIR

DB = CONFIG_DIR / "memory.db"

def _db():
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB)
    con.execute("CREATE TABLE IF NOT EXISTS memories (id INTEGER PRIMARY KEY, created REAL, key TEXT, value TEXT)")
    return con

def memory(action: str, key: str | None = None, value: str | None = None):
    con = _db()
    try:
        if action == "set":
            if not key or value is None:
                return {"ok": False, "error": "set requires key and value"}
            con.execute("INSERT INTO memories(created,key,value) VALUES(?,?,?)", (time.time(), key, value))
            con.commit()
            return {"ok": True}
        if action == "get":
            if not key:
                return {"ok": False, "error": "get requires key"}
            rows = con.execute("SELECT id,created,key,value FROM memories WHERE key=? ORDER BY id DESC LIMIT 20",(key,)).fetchall()
            return {"ok": True, "items": rows}
        if action == "search":
            q = f"%{value or key or ''}%"
            rows = con.execute("SELECT id,created,key,value FROM memories WHERE key LIKE ? OR value LIKE ? ORDER BY id DESC LIMIT 50",(q,q)).fetchall()
            return {"ok": True, "items": rows}
        if action == "list":
            rows = con.execute("SELECT id,created,key,value FROM memories ORDER BY id DESC LIMIT 50").fetchall()
            return {"ok": True, "items": rows}
        return {"ok": False, "error": "action must be set|get|search|list"}
    finally:
        con.close()

def tool():
    return Tool("memory", "Store and recall persistent information across FORGE sessions.", {
        "type":"object",
        "properties":{
            "action":{"type":"string","enum":["set","get","search","list"]},
            "key":{"type":["string","null"]},
            "value":{"type":["string","null"]}
        },
        "required":["action"],
        "additionalProperties":False
    }, memory, "memory")
