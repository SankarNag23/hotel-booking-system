#!/bin/bash
set -e

# Create dist directory
mkdir -p dist

# Copy all files from public to dist
cp -r public/* dist/

# Ensure proper permissions
chmod -R 755 dist/

echo "Static build completed successfully!" 