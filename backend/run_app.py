"""Runner script for production hosting (e.g., Render).

Usage (Render start command):
    python backend/run_app.py

It reads PORT from the environment (default 8000) and starts Uvicorn.
"""
import os
import uvicorn


def main():
    port = int(os.getenv("PORT", "8000"))
    host = os.getenv("HOST", "0.0.0.0")
    # The app import path expected by uvicorn here is backend.simple_main:app
    uvicorn.run("backend.simple_main:app", host=host, port=port, log_level="info")


if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Simple runner for the Hermes FastAPI application.
This handles the import paths and runs the app directly.
"""

import sys
import os
import uvicorn

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Import the app
try:
    from backend.app import app
    print("✅ Successfully imported backend.app")
except ImportError as e:
    print(f"❌ Failed to import backend.app: {e}")
    print("Falling back to simple_main...")
    from backend.simple_main import app

if __name__ == "__main__":
    print("🚀 Starting Hermes Trading Companion API...")
    print("📊 SQLite fallback database active")
    print("🌐 Server will be available at http://localhost:8000")
    print("📖 API docs at http://localhost:8000/docs")
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000, 
        reload=False  # Disable reload to avoid import issues
    )
