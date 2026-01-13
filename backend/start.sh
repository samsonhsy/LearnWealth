#!/bin/bash
# Render startup script
# This ensures PORT is properly passed to uvicorn

# Debug: Print all environment variables related to port
echo "DEBUG: Environment variables:"
env | grep -i port || echo "No PORT variables found"
echo "PORT=$PORT"
echo "WEB_PORT=$WEB_PORT"

# Render might use PORT or WEB_PORT
if [ -n "$PORT" ]; then
    ACTUAL_PORT=$PORT
elif [ -n "$WEB_PORT" ]; then
    ACTUAL_PORT=$WEB_PORT
else
    ACTUAL_PORT=8000
fi

echo "Starting server on port $ACTUAL_PORT"
exec uv run uvicorn main:app --host 0.0.0.0 --port $ACTUAL_PORT
