#!/bin/bash

# Exit on error
set -e

echo "🚀 Starting deployment process..."

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Git is not installed. Please install git first."
    exit 1
fi

# Check if render-cli is installed
if ! command -v render &> /dev/null; then
    echo "📦 Installing render-cli..."
    curl -o render-cli https://render.com/download/render-cli/render-cli
    chmod +x render-cli
    sudo mv render-cli /usr/local/bin/render
fi

# Check if we're in a git repository
if [ ! -d .git ]; then
    echo "❌ Not a git repository. Initializing..."
    git init
fi

# Add all files
echo "📦 Adding files to git..."
git add .

# Commit changes
echo "💾 Committing changes..."
git commit -m "Deploy to Render.com"

# Push to main branch
echo "🚀 Pushing to main branch..."
git push origin main

echo "✅ Deployment process completed!"
echo "🔍 Check your Render.com dashboard for deployment status." 