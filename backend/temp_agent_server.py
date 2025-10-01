from fastapi import FastAPI
import uvicorn
import sys

app = FastAPI()

# Import the agent router directly from backend. Avoid top-level imports that fail in full app.
from routers import agent as agent_router

app.include_router(agent_router.router, prefix="/api")

if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=8002)
