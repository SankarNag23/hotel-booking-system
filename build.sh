#!/bin/bash
set -e

# Upgrade pip
python -m pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Start the application using gunicorn
exec python -m gunicorn wsgi:app --bind 0.0.0.0:$PORT --workers 1 --timeout 120 --log-level debug 