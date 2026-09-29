"""Smoke test: runs the full agent loop against a stub Ollama server.

This validates the provider's request/response handling and the agent's
tool loop without needing a real model. Run with:

    python smoke_test.py
"""
import json
import os
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from harness import Agent, Config  # noqa: E402

STATE = {"chats": 0}


class StubOllama(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _send(self, obj):
        body = json.dumps(obj).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/api/tags":
            self._send({"models": [{"name": "qwen2.5:3b"}]})
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        payload = json.loads(self.rfile.read(length) or b"{}")
        assert payload["model"] == "qwen2.5:3b", "model not passed through"
        assert payload["tools"], "tools not passed through"
        assert payload["stream"] is False
        STATE["chats"] += 1
        if STATE["chats"] == 1:
            # First turn: call a tool (string args, as some servers send)
            self._send({"message": {
                "role": "assistant",
                "content": "I'll write a file.",
                "tool_calls": [{"function": {
                    "name": "file_write",
                    "arguments": json.dumps({"path": "smoke.txt", "content": "smoke ok"}),
                }}],
            }})
        elif STATE["chats"] == 2:
            # Verify the tool result came back as a tool message
            tool_msgs = [m for m in payload["messages"] if m.get("role") == "tool"]
            assert tool_msgs and "Wrote" in tool_msgs[0]["content"], f"bad tool echo: {tool_msgs}"
            self._send({"message": {"role": "assistant", "content": "Done, file written."}})
        else:
            raise AssertionError("too many chat turns")


def main():
    server = HTTPServer(("127.0.0.1", 0), StubOllama)
    port = server.server_address[1]
    threading.Thread(target=server.serve_forever, daemon=True).start()

    cfg = Config()
    cfg.host = f"http://127.0.0.1:{port}"
    cfg.model = "qwen2.5:3b"
    cfg.workspace = "/tmp/harness-smoke-ws"
    agent = Agent(cfg)
    out = agent.run("write a smoke test file")
    assert out.strip() == "Done, file written.", f"unexpected final: {out!r}"
    with open("/tmp/harness-smoke-ws/smoke.txt") as f:
        assert f.read() == "smoke ok"
    server.shutdown()
    print("SMOKE TEST PASSED")


if __name__ == "__main__":
    main()
