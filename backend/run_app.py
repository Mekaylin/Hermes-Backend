#!/usr/bin/env python3
"""Runner script for production hosting (e.g., Render).

Usage (Render start command):
    python backend/run_app.py

It reads PORT from the environment (default 8000) and starts Uvicorn.
"""
import sys
import os
import uvicorn

# Add the project root to Python path so backend imports work
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def main():
    port = int(os.getenv("PORT", "8000"))
    host = os.getenv("HOST", "0.0.0.0")
    
    # Import the app
    try:
        from backend.simple_main import app
        print("✅ Successfully imported backend.simple_main")
    except ImportError as e:
        print(f"❌ Failed to import backend.simple_main: {e}")
        sys.exit(1)
    
    print("🚀 Starting Hermes Trading Companion API...")
    print(f"🌐 Server will be available at http://{host}:{port}")
    print(f"📖 API docs at http://{host}:{port}/docs")
    
    # Run the app
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info",
        reload=False
    )

if __name__ == "__main__":
    main()
