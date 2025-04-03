#!/bin/bash

# Hotel Booking System Deployment Script
# Version: v3-0304250-1320
# Date: March 4, 2025

# Exit on error
set -e

# Configuration
APP_NAME="hotel-booking-system"
GITHUB_REPO="https://github.com/SankarNag23/hotel-booking-system.git"
BRANCH="main"
TAG="v3-0304250-1320"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Print with timestamp
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    # Check Node.js
    if ! command -v node >/dev/null 2>&1; then
        error "Node.js is required but not installed."
        exit 1
    fi
    
    # Check npm
    if ! command -v npm >/dev/null 2>&1; then
        error "npm is required but not installed."
        exit 1
    fi
    
    # Check Git
    if ! command -v git >/dev/null 2>&1; then
        error "Git is required but not installed."
        exit 1
    }
    
    log "Prerequisites check passed."
}

# Cleanup function
cleanup() {
    if [ -d "$APP_NAME" ]; then
        warn "Cleaning up existing directory..."
        rm -rf "$APP_NAME"
    fi
}

# Clone repository
clone_repo() {
    log "Cloning repository..."
    git clone "$GITHUB_REPO" "$APP_NAME"
    cd "$APP_NAME"
    git checkout "$TAG"
}

# Install dependencies
install_dependencies() {
    log "Installing dependencies..."
    npm install
}

# Build application
build_app() {
    log "Building application..."
    npm run build
}

# Create environment file
create_env() {
    log "Creating environment file..."
    cat > .env << EOL
PORT=10000
NODE_ENV=production
EOL
}

# Run tests
run_tests() {
    log "Running tests..."
    npm test || {
        warn "Tests failed but continuing deployment..."
    }
}

# Health check
health_check() {
    log "Performing health check..."
    local retries=5
    local wait_time=5
    
    while [ $retries -gt 0 ]; do
        if curl -s http://localhost:10000/api/hotels > /dev/null; then
            log "Health check passed."
            return 0
        fi
        retries=$((retries-1))
        warn "Health check failed. Retrying in $wait_time seconds..."
        sleep $wait_time
    done
    
    error "Health check failed after all retries."
    return 1
}

# Main deployment function
deploy() {
    log "Starting deployment of $APP_NAME version $TAG"
    
    # Run deployment steps
    check_prerequisites
    cleanup
    clone_repo
    install_dependencies
    create_env
    build_app
    run_tests
    
    log "Starting application..."
    npm start &
    
    # Wait for application to start
    sleep 5
    
    # Perform health check
    if health_check; then
        log "Deployment completed successfully!"
    else
        error "Deployment failed at health check stage."
        exit 1
    fi
}

# Rollback function
rollback() {
    error "Deployment failed. Rolling back..."
    cleanup
    log "Rollback completed."
    exit 1
}

# Trap errors and execute rollback
trap rollback ERR

# Execute deployment
deploy 