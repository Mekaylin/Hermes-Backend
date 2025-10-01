Dev Control Page
================

This project includes a developer control page at /dev-control which lets you:

- Copy a recommended command to start the backend locally.
- Trigger simple simulated training and testing endpoints exposed by the backend:
  - POST /api/agent/train
  - POST /api/agent/test

Usage (development):

1. Start the backend (from project root):
   cd backend
   ./venv/bin/python -m uvicorn backend.simple_main:app --reload --port 8001

2. Start the frontend:
   cd react-frontend
   npm install
   npm run dev

3. Open http://localhost:5173/dev-control (or the dev server port shown by Vite)

Notes:
- The DevControl page expects the backend to be reachable at http://localhost:8001 during development. If your backend runs at a different port, modify the fetch base URL in src/pages/DevControl.tsx.
- The backend's training endpoint is a simulated helper (backend/ai_training.py) and does not run heavy ML training by default.
