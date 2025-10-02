# Minimal stub for agents package used by visualization
from typing import Any


class MCPServer: ...


class extensions:
    class visualization:
        def draw_graph(self, obj: Any, format: str = 'png') -> bytes: ...
    

class Agent:
    def __init__(self, *args, **kwargs): ...


def function_tool(fn: Any) -> Any: ...
