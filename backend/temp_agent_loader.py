import importlib.util
import sys
from fastapi import FastAPI
import uvicorn
from pathlib import Path

BASE = Path(__file__).parent
AGENT_PATH = BASE / 'routers' / 'agent.py'

spec = importlib.util.spec_from_file_location('agent_router_mod', str(AGENT_PATH))
agent_mod = importlib.util.module_from_spec(spec)
sys.modules['agent_router_mod'] = agent_mod
spec.loader.exec_module(agent_mod)

app = FastAPI()
app.include_router(agent_mod.router, prefix='/api')

if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=8003)
