# Deploying Hermes Backend to Render

Quick steps to deploy the FastAPI backend to Render:

1. Add this repo to GitHub and connect it to Render.

2. Create a new Web Service on Render.

3. Build Command:

```bash
pip install -r requirements.txt
```

4. Start Command:

```bash
python backend/run_app.py
```

5. Environment variables:

- Add your `OPENAI_API_KEY`, `NEWS_API_KEY`, `DATABASE_URL`, and any other secrets in Render's dashboard under Environment.
- Ensure you do NOT push `.env` to the repo (it's in `.gitignore`).

6. Ports:

Render sets `PORT` automatically in the environment; `backend/run_app.py` reads `PORT` and binds to it.

7. Health check:

Visit `https://<your-service>.onrender.com/health` after deploy to verify the app is running.

Notes:
- If using Graphviz rendering on Render, the `dot` binary must be available. Consider using a prebuilt Render image with Graphviz or render graphs server-side and store them as static assets.
- For production, pin package versions carefully and use a requirements lock (pip-compile / pip freeze) for deterministic builds.
