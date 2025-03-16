#!/usr/bin/env bash
# exit on error
set -o errexit

# Install system dependencies required for building wheels
apt-get update
apt-get install -y python3-dev build-essential

# Upgrade pip and install wheel
pip install --upgrade pip
pip install wheel

# Install Python packages
pip install -r requirements.txt 