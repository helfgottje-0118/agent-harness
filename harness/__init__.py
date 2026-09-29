"""Agent harness: a minimal ReAct-style agent loop with pluggable tools,
backed by Ollama for the model."""
from .agent import Agent
from .config import Config

__all__ = ["Agent", "Config"]
