"""CLI: single-shot task or interactive REPL.

Usage:
    python -m harness.cli "summarize the repo in ./work"
    python -m harness.cli --model qwen3:8b --verbose
"""
from __future__ import annotations

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from harness import Agent, Config


def _print_event(kind: str, data: dict) -> None:
    if kind == "assistant" and data.get("content"):
        print(f"\n[agent] {data['content']}\n")
    elif kind == "tool_call":
        print(f"[tool] {data['name']}({', '.join(f'{k}={v!r}' for k, v in data['arguments'].items())})")
    elif kind == "tool_result":
        print(f"[result]\n{data['result']}\n")


def build_config(args) -> Config:
    cfg = Config()
    if args.host:
        cfg.host = args.host
    if args.model:
        cfg.model = args.model
    if args.max_iters:
        cfg.max_iterations = args.max_iters
    if args.workspace:
        cfg.workspace = args.workspace
    if args.verbose:
        cfg.verbose = True
    return cfg


def main() -> None:
    p = argparse.ArgumentParser(description="Agent harness (Ollama-backed)")
    p.add_argument("task", nargs="?", help="Task to run. Omit for interactive mode.")
    p.add_argument("--model", help="Ollama model (default from OLLAMA_MODEL or qwen2.5:3b)")
    p.add_argument("--host", help="Ollama host (default from OLLAMA_HOST or http://localhost:11434)")
    p.add_argument("--max-iters", type=int, help="Max agent loop iterations")
    p.add_argument("--workspace", help="Workspace dir for file/shell tools")
    p.add_argument("--verbose", action="store_true", help="Print live agent/tool feed")
    args = p.parse_args()

    cfg = build_config(args)
    agent = Agent(cfg)
    on_event = _print_event if cfg.verbose else None

    if args.task:
        print(agent.run(args.task, on_event=on_event))
        return

    print(f"agent-harness — model {cfg.model} @ {cfg.host} (type 'exit' to quit)")
    while True:
        try:
            task = input("\n> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if task.lower() in ("exit", "quit"):
            break
        if not task:
            continue
        try:
            print(agent.run(task, on_event=_print_event))
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()
