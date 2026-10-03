from .base import ToolRegistry
from .terminal import build_terminal_tool
from .files import tools as file_tools
from .memory import tool as memory_tool

def build_registry(config):
    r = ToolRegistry()
    r.register(build_terminal_tool(config))
    for t in file_tools():
        r.register(t)
    r.register(memory_tool())
    return r
