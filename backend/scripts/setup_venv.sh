#!/usr/bin/env bash
set -euo pipefail

# Creates a Python venv in .venv and installs backend/requirements.txt
# Usage: ./scripts/setup_venv.sh

PYTHON=${PYTHON:-python3}
VENV_DIR=".venv"

if [ -d "$VENV_DIR" ]; then
  echo "Using existing venv at $VENV_DIR"
else
  echo "Creating virtualenv at $VENV_DIR..."
  python -m venv "$VENV_DIR"
  echo "Activating venv and installing requirements..."
  . "$VENV_DIR/bin/activate"
  python -m pip install --upgrade pip
  if [ -f requirements.txt ]; then
    pip install -r requirements.txt
  else
    echo "No requirements.txt found in backend/ — skipping install."
  fi
  echo "Done. Activate with: source $VENV_DIR/bin/activate"
  
  # Recommended Python: 3.11 (some packages e.g. SQLAlchemy/Alembic are known to be
  # incompatible with newer CPython minor releases in certain environments).
  
  PY_VERSION=$(python -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")') || true
  echo "Detected Python version: $PY_VERSION"
  if [[ "$PY_VERSION" != "3.11" ]]; then
    echo "Warning: this project recommends Python 3.11 for best compatibility." >&2
    echo "If you encounter SQLAlchemy/Alembic import errors, create a 3.11 venv and re-run this script." >&2
  fi
  
  echo "Setup complete. Activate with: source $VENV_DIR/bin/activate"
fi

# Activate and install
source "$VENV_DIR/bin/activate"
python -m pip install --upgrade pip
pip install -r requirements.txt

echo "Setup complete. Activate with: source $VENV_DIR/bin/activate"
