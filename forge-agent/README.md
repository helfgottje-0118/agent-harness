# FORGE Agent

**FORGE = Framework for Orchestrated Reasoning, Generation & Execution**

A clean-room, extensible AI agent harness inspired by the interaction model of terminal-first agents such as Hermes.

## Current working features

- `forge`
- `forge chat`
- `forge chat -q "..."`
- `forge tools`
- `forge model`
- `forge setup`
- OpenAI-compatible chat-completions provider
- Ollama through its OpenAI-compatible endpoint
- Tool registry
- Toolset selection
- Local terminal execution
- Read/write/patch-like text replacement file tools
- SQLite persistent memory
- Config profiles
- Automatic tool-calling loop for OpenAI-compatible models that support tools

## Install

```bash
cd forge-agent
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
forge setup
forge tools
forge chat
```

### Ollama example

```yaml
provider:
  name: openai_compatible
  base_url: http://127.0.0.1:11434/v1
  api_key: ollama
  model: qwen3.5:latest
```

## Examples

```bash
forge chat -q "Use terminal to run pwd and uname -a"
forge chat --toolsets terminal,file -q "Create /tmp/forge-test.txt containing hello"
forge tools
forge model
```

## Security

The `terminal` tool executes real commands on the configured machine. Use a Docker/SSH backend before exposing FORGE to untrusted prompts.
