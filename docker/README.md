Local Docker for Hermes (Postgres + Redis)

This folder contains a simple docker-compose for local development.

Start services:

  docker compose -f ../dev-docker-compose.yml up -d

Stop services:

  docker compose -f ../dev-docker-compose.yml down

Environment variables to set for the backends (example):

  export DATABASE_URL=postgresql+psycopg2://hermes:hermes_password@localhost:5432/hermes
  export REDIS_URL=redis://localhost:6379/0

Notes:
- This is optional for local development; the project supports a SQLite fallback and mock-mode.
- Docker must be installed locally to use this convenience compose file.
