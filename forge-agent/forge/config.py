from __future__ import annotations
from pathlib import Path
import os, yaml

CONFIG_DIR = Path(os.environ.get("FORGE_HOME", Path.home() / ".forge"))
CONFIG_PATH = CONFIG_DIR / "config.yaml"

DEFAULT_CONFIG = {
    "provider": {
        "name": "openai_compatible",
        "base_url": "http://127.0.0.1:11434/v1",
        "api_key": "ollama",
        "model": "qwen3.5:latest",
    },
    "agent": {
        "max_tool_rounds": 12,
        "system_prompt": (
            "You are FORGE, an autonomous AI agent. "
            "Use tools when they are the most reliable way to complete work. "
            "Do not claim a tool action happened unless the tool result confirms it."
        ),
    },
    "terminal": {
        "backend": "local",
        "cwd": ".",
        "timeout": 180,
    },
    "platform_toolsets": {
        "forge-cli": ["terminal", "file", "memory"]
    }
}

def ensure_config():
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    if not CONFIG_PATH.exists():
        CONFIG_PATH.write_text(yaml.safe_dump(DEFAULT_CONFIG, sort_keys=False))
    return CONFIG_PATH

def load_config():
    ensure_config()
    data = yaml.safe_load(CONFIG_PATH.read_text()) or {}
    return merge(DEFAULT_CONFIG, data)

def merge(a, b):
    if isinstance(a, dict) and isinstance(b, dict):
        out = dict(a)
        for k, v in b.items():
            out[k] = merge(out[k], v) if k in out else v
        return out
    return b
