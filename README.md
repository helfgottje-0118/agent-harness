# Agent Harness

A minimal, hackable AI agent harness: a ReAct-style loop (`model → tool calls → model …`)
with **shell**, **file**, and **web** tools, backed by **Ollama**.

## Setup

1. Install Ollama and pull a tool-capable model:
   ```bash
   ollama pull qwen2.5:3b
   ```
   (Any tool-calling model works: `qwen3`, `llama3.1`, `mistral-nemo`, …)

2. Install the one dependency:
   ```bash
   pip install -r requirements.txt
   ```

3. Make sure Ollama is serving (`ollama serve`, or it starts on demand).

## Usage

Single task:
```bash
python -m harness.cli "list the files in the workspace and summarize README.md" --verbose
```

Interactive mode:
```bash
python -m harness.cli --model qwen3:8b
```

Options can also come from the environment:

| Variable | Default | Meaning |
|---|---|---|
| `OLLAMA_HOST` | `http://localhost:11434` | Where Ollama serves (point at another machine if needed) |
| `OLLAMA_MODEL` | `qwen2.5:3b` | Model to use (must support tools) |
| `HARNESS_MAX_ITERS` | `15` | Max loop iterations per task |
| `HARNESS_TOOL_TIMEOUT` | `60` | Per-tool timeout, seconds |
| `HARNESS_WORKSPACE` | `~/workspace/agent-harness/work` | Sandbox for file/shell tools |
| `HARNESS_VERBOSE` | `0` | Set `1` for a live tool-call feed |

## Tools

| Tool | What it does |
|---|---|
| `shell_exec` | Run a shell command in the workspace (timeouts, output truncation, destructive-pattern blocklist) |
| `file_read` / `file_write` / `file_edit` / `file_list` | File ops sandboxed to the workspace (path traversal rejected) |
| `web_fetch` | Fetch a URL, return readable text |
| `web_search` | Web search via DuckDuckGo HTML (no API key; best-effort) |

## Testing without a model

`smoke_test.py` runs the full agent loop against a stub Ollama server, so you
can verify the wiring without pulling a model:

```bash
python smoke_test.py
```

## Layout

```
harness/
  agent.py        # the ReAct loop
  config.py       # env-based config
  cli.py          # single-shot + REPL
  providers/
    ollama.py     # Ollama /api/chat with tool calling
  tools/
    __init__.py   # Tool + ToolRegistry, default toolset wiring
    shell.py      # shell_exec
    files.py      # sandboxed file ops
    web.py        # web_fetch, web_search
work/             # default agent workspace
```

## Extending

Add a tool by registering it in `build_default_registry()` (in `harness/tools/__init__.py`):
a name, a description, a JSON-Schema `parameters` dict, and a Python function
returning a string. The agent picks it up automatically — no other changes needed.
