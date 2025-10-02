FROM python:3.11-slim

# Install system dependencies required for some Python packages and for graphviz
RUN apt-get update \
	&& DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
	   build-essential \
	   libpq-dev \
	   graphviz \
	   git \
	   curl \
	&& rm -rf /var/lib/apt/lists/*

ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Copy only the backend requirements and install (build context is the repo root)
COPY backend/requirements.txt ./requirements.txt
RUN python -m pip install --upgrade pip setuptools wheel \
	&& pip install --no-cache-dir -r requirements.txt

# Copy backend source only
COPY backend/ ./backend/

# Default command: run the backend runner which reads $PORT
CMD ["python", "backend/run_app.py"]
