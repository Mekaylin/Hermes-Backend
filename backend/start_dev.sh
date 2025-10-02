#!/bin/bash
# Quick start script for backend during development

cd "$(dirname "$0")"
.venv/bin/python3 -m uvicorn simple_main:app --host 0.0.0.0 --port 8000 --reload
