#!/usr/bin/env python3
import os
import sys
import subprocess

# Get port from environment, Render uses PORT or WEB_PORT
port = os.environ.get('PORT') or os.environ.get('WEB_PORT') or '8000'

print(f"Starting server on port {port}")
sys.stdout.flush()

# Run uvicorn
cmd = [
    'uv', 'run', 'uvicorn', 
    'main:app', 
    '--host', '0.0.0.0', 
    '--port', port
]

subprocess.run(cmd)
