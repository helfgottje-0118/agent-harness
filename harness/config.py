"""Configuration, sourced from environment variables with sane defaults."""
import os
from dataclasses import dataclass, field


@dataclass
class Config:
    # Where Ollama serves its API. Point at your machine if Ollama runs elsewhere,
    # e.g. OLLAMA_HOST=http://192.168.1.10:11434
    host: str = field(default_factory=lambda: os.environ.get("OLLAMA_HOST", "http://localhost:11434"))
    # Model must support tool calling, e.g. qwen2.5, qwen3, llama3.1, llama3.2, mistral-nemo
    model: str = field(default_factory=lambda: os.environ.get("OLLAMA_MODEL", "qwen2.5:3b"))
    # Max agent loop iterations before giving up
    max_iterations: int = field(default_factory=lambda: int(os.environ.get("HARNESS_MAX_ITERS", "15")))
    # Per-tool-call timeout in seconds
    tool_timeout: int = field(default_factory=lambda: int(os.environ.get("HARNESS_TOOL_TIMEOUT", "60")))
    # File tools are sandboxed to this directory (path traversal is rejected)
    workspace: str = field(
        default_factory=lambda: os.environ.get(
            "HARNESS_WORKSPACE",
            os.path.join(os.path.expanduser("~"), "workspace", "agent-harness", "work"),
        )
    )
    verbose: bool = field(default_factory=lambda: os.environ.get("HARNESS_VERBOSE", "0") == "1")
