"""
Main entry point for the Hotel Booking System
"""

from fastapi import FastAPI, Request, HTTPException, Depends, Security
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import uvicorn
import os
import logging
from datetime import datetime, timedelta
import random
import string
import httpx
from app.hotel_booking_system_v2 import UserInterfaceAgent, BookingAPIAgent, IntegrationAgent
from dotenv import load_dotenv
from app.hotel_providers import HotelDataProvider
from app.middleware import SecurityHeadersMiddleware
from app.validators import BookingRequest, sanitize_search_params, validate_api_key, validate_hotel_id, sanitize_log_data
from fastapi.security import APIKeyHeader
from fastapi.security.api_key import APIKey
from starlette.status import HTTP_403_FORBIDDEN
import secrets
import re
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Hotel Booking System",
    description="A modern hotel booking system with advanced features",
    version="2.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("ALLOWED_ORIGINS", "http://localhost:8000")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add security headers middleware
app.add_middleware(SecurityHeadersMiddleware)

# Get API keys from environment variables
BOOKING_API_KEY = os.getenv("BOOKING_API_KEY")
GOOGLE_HOTELS_API_KEY = os.getenv("GOOGLE_HOTELS_API_KEY")
GOOGLE_HOTELS_CLIENT_ID = os.getenv("GOOGLE_HOTELS_CLIENT_ID")

# Check if Google Hotels API credentials are available
GOOGLE_HOTELS_AVAILABLE = bool(GOOGLE_HOTELS_API_KEY and GOOGLE_HOTELS_CLIENT_ID)

# Get absolute paths for static files and templates
current_dir = os.path.dirname(os.path.abspath(__file__))
static_dir = os.path.join(current_dir, "app", "static")
templates_dir = os.path.join(current_dir, "app", "templates")

# Create directories if they don't exist
os.makedirs(static_dir, exist_ok=True)
os.makedirs(templates_dir, exist_ok=True)

# Mount static files and templates
app.mount("/static", StaticFiles(directory=static_dir, html=True), name="static")
templates = Jinja2Templates(directory=templates_dir)

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Render the home page"""
    return templates.TemplateResponse("index.html", {"request": request, "version": "2.1.0"})

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": "2.1.0"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 