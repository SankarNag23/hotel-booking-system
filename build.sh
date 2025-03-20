#!/bin/bash
set -e

# Upgrade pip
python -m pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Start the application
exec python -m gunicorn app:app --bind 0.0.0.0:$PORT --workers 4 --timeout 120 --log-level info 