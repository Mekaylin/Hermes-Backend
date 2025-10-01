Deploying the Hermes backend to Render

Quick start

1. Copy the example env and fill it:

   cp backend/.env.example backend/.env
   # Fill backend/.env with your keys (do NOT commit this file)

2. Push your code to GitHub and ensure the `render.yaml` is at the repo root.

3. In Render, create a new web service and choose "Deploy from Git". Select the repo and branch `master` (or change in `render.yaml`).

4. Render will use `backend/Dockerfile` (Docker build). Set environment variables in Render's dashboard (do NOT upload the .env file). At minimum set `OPENAI_API_KEY` and any DB/Redis URLs or other secrets.

5. Health check

   The service exposes a health endpoint at `/api/agent/health` (configured in `render.yaml`).

Troubleshooting

- If builds fail due to missing system packages (e.g., libpq for psycopg2), add apt packages to the Dockerfile or switch to the build image that includes required libs.
- If the app requires GPU or large memory for transformers, consider using a proper plan on Render or offloading heavy inference to a separate service.

Security

- Do NOT commit `backend/.env`. Use Render's dashboard to inject secrets. `backend/.env.example` documents variables expected by the app.
