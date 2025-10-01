from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
import os
import tempfile

router = APIRouter(prefix="/agents", tags=["Agent Visualization"])


@router.get("/visualize", summary="Generate agent graph PNG")
def visualize_agent_graph():
    """Generate a sample agent graph PNG and return it as image/png.

    This uses the openai-agents visualization helper to draw a small
    triage agent with handoffs and a sample tool. The function writes
    the graph to a temporary file and returns the PNG bytes.
    """
    try:
        # Lazy import optional visualization dependency
        from agents import Agent, function_tool
        from agents.mcp.server import MCPServerStdio
        from agents.extensions.visualization import draw_graph

        @function_tool
        def get_weather(city: str) -> str:
            return f"The weather in {city} is sunny."

        spanish_agent = Agent(name="Spanish agent", instructions="You only speak Spanish.")
        english_agent = Agent(name="English agent", instructions="You only speak English")

        current_dir = os.path.dirname(__file__)
        samples_dir = os.path.join(current_dir, "..", "..", "samples")
        mcp_server = MCPServerStdio(name="Filesystem Server, via npx", params={
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-filesystem", samples_dir],
        })

        triage_agent = Agent(
            name="Triage agent",
            instructions="Handoff to the appropriate agent based on the language of the request.",
            handoffs=[spanish_agent, english_agent],
            tools=[get_weather],
            mcp_servers=[mcp_server],
        )

        # Draw graph to a temporary filename
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            filename = tmp.name

        graph = draw_graph(triage_agent, filename=filename)
        # graph.render() may be called by draw_graph internally; ensure file exists
        if not os.path.exists(filename):
            # Some draw_graph implementations return the graph object but write a .png with that name
            png_path = filename
        else:
            png_path = filename

        with open(png_path, 'rb') as f:
            data = f.read()

        # Clean up the temp file
        try:
            os.remove(png_path)
        except Exception:
            pass

        return Response(content=data, media_type='image/png')

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate graph: {str(e)}")
