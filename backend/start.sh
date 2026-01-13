#!/bin/bash
# Render startup script
# This ensures PORT is properly passed to uvicorn

# Render might use PORT or WEB_PORT
PORT=${PORT:-${WEB_PORT:-8000}}
echo "Starting server on port $PORT"
exec uv run uvicorn main:app --host 0.0.0.0 --port "$PORT"
