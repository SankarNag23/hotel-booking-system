#!/bin/bash
set -e

# Upgrade pip
python -m pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
