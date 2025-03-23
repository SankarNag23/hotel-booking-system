from flask import Flask, request, render_template, jsonify
from flask_cors import CORS
from pydantic import BaseModel
from typing import List, Dict, Optional
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

app = Flask(__name__)
CORS(app)

# Mount static files
app.static_folder = 'static'
app.template_folder = 'templates'

# Get API keys from environment variables with validation
BOOKING_API_KEY = os.getenv("BOOKING_API_KEY")
GOOGLE_HOTELS_API_KEY = os.getenv("GOOGLE_HOTELS_API_KEY")
GOOGLE_HOTELS_CLIENT_ID = os.getenv("GOOGLE_HOTELS_CLIENT_ID")

if not validate_api_key(BOOKING_API_KEY):
    logger.error("Invalid or missing BOOKING_API_KEY")
    raise ValueError("Invalid or missing BOOKING_API_KEY")

# Check if Google Hotels API credentials are available
GOOGLE_HOTELS_AVAILABLE = bool(GOOGLE_HOTELS_API_KEY and GOOGLE_HOTELS_CLIENT_ID)

# Get absolute paths for static files and templates
current_dir = os.path.dirname(os.path.abspath(__file__))
static_dir = os.path.join(current_dir, "static")
templates_dir = os.path.join(current_dir, "templates")

# Create directories if they don't exist
os.makedirs(static_dir, exist_ok=True)
os.makedirs(templates_dir, exist_ok=True)

# Ensure index.html exists
index_template = os.path.join(templates_dir, "index.html")
if not os.path.exists(index_template):
    with open(index_template, "w") as f:
        f.write("""
<!DOCTYPE html>
<html>
<head>
    <title>Hotel Booking System</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body>
    <h1>Hotel Booking System</h1>
    <p>System is running. Please use the API endpoints.</p>
</body>
</html>
        """.strip())

try:
    # Initialize templates
    templates = Jinja2Templates(directory=templates_dir)
    logger.info(f"Successfully initialized static files and templates")
except Exception as e:
    logger.warning(f"Error mounting static files: {str(e)}")
    # Continue without static files if there's an error

# Initialize agents with error handling
try:
    ui_agent = UserInterfaceAgent()
    booking_agent = BookingAPIAgent(api_key=BOOKING_API_KEY)
    integration_agent = IntegrationAgent(api_key=BOOKING_API_KEY)
    logger.info("Agents initialized successfully")
except Exception as e:
    logger.error(f"Error initializing agents: {str(e)}")
    raise

# Google Hotels API endpoints
GOOGLE_HOTELS_BASE_URL = "https://hotels.googleapis.com/v1"
GOOGLE_HOTELS_CONTENT_URL = f"{GOOGLE_HOTELS_BASE_URL}/hotelContent"
GOOGLE_HOTELS_PRICES_URL = f"{GOOGLE_HOTELS_BASE_URL}/hotelPrices"

# Mock hotel database with more detailed information
HOTELS = {
    "new york": [
        {
            "id": "ny1",
            "name": "Grand Central Hotel",
            "address": "123 Park Avenue, New York, NY 10017",
            "stars": 5,
            "rating": 4.8,
            "reviews": 1250,
            "description": "Luxury hotel in the heart of Manhattan, offering stunning views of Central Park.",
            "price_per_night": 450,
            "room_types": ["Standard", "Deluxe", "Suite", "Presidential"],
            "amenities": ["pool", "breakfast", "parking", "wifi", "fitness", "spa", "restaurant", "bar"],
            "image_url": "https://images.unsplash.com/photo-1542314831-068cd1dbfeeb?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80",
            "highlights": ["Central Park View", "Luxury Spa", "Fine Dining"],
            "location": "Manhattan",
            "nearby_attractions": ["Central Park", "Times Square", "Fifth Avenue"]
        },
        {
            "id": "ny2",
            "name": "Times Square Inn",
            "address": "456 Broadway, New York, NY 10036",
            "stars": 4,
            "rating": 4.2,
            "reviews": 980,
            "description": "Modern hotel in the heart of Times Square, perfect for business and leisure travelers.",
            "price_per_night": 350,
            "room_types": ["Standard", "Deluxe", "Suite"],
            "amenities": ["breakfast", "wifi", "fitness", "restaurant"],
            "image_url": "https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80",
            "highlights": ["Times Square Location", "Business Center", "24/7 Gym"],
            "location": "Times Square",
            "nearby_attractions": ["Times Square", "Broadway", "Empire State Building"]
        }
    ],
    "london": [
        {
            "id": "ldn1",
            "name": "Royal Park Hotel",
            "address": "1 Hyde Park Corner, London SW1X 7TA",
            "stars": 5,
            "rating": 4.9,
            "reviews": 850,
            "description": "Elegant hotel overlooking Hyde Park, offering traditional British luxury.",
            "price_per_night": 500,
            "room_types": ["Standard", "Deluxe", "Suite", "Presidential"],
            "amenities": ["pool", "breakfast", "parking", "wifi", "fitness", "spa", "restaurant", "bar", "conference"],
            "image_url": "https://images.unsplash.com/photo-1566073771259-6a8506099945?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80",
            "highlights": ["Hyde Park View", "Traditional Afternoon Tea", "Luxury Spa"],
            "location": "Hyde Park",
            "nearby_attractions": ["Hyde Park", "Buckingham Palace", "Harrods"]
        }
    ],
    "paris": [
        {
            "id": "prs1",
            "name": "Eiffel View Hotel",
            "address": "15 Avenue de Suffren, 75007 Paris",
            "stars": 4,
            "rating": 4.5,
            "reviews": 720,
            "description": "Charming hotel with stunning views of the Eiffel Tower.",
            "price_per_night": 400,
            "room_types": ["Standard", "Deluxe", "Suite"],
            "amenities": ["breakfast", "wifi", "fitness", "restaurant", "bar"],
            "image_url": "https://images.unsplash.com/photo-1502602898657-3e91760cbb34?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80",
            "highlights": ["Eiffel Tower View", "French Cuisine", "Rooftop Bar"],
            "location": "7th Arrondissement",
            "nearby_attractions": ["Eiffel Tower", "Champ de Mars", "Musée d'Orsay"]
        }
    ],
    "tokyo": [
        {
            "id": "tky1",
            "name": "Sakura Garden Hotel",
            "address": "2-1-1 Marunouchi, Chiyoda-ku, Tokyo 100-0005",
            "stars": 5,
            "rating": 4.7,
            "reviews": 650,
            "description": "Modern luxury hotel combining traditional Japanese aesthetics with contemporary design.",
            "price_per_night": 550,
            "room_types": ["Standard", "Deluxe", "Suite", "Presidential"],
            "amenities": ["pool", "breakfast", "parking", "wifi", "fitness", "spa", "restaurant", "bar", "conference"],
            "image_url": "https://images.unsplash.com/photo-1542051841857-5f90071e7989?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80",
            "highlights": ["Traditional Onsen", "Michelin Restaurant", "Zen Garden"],
            "location": "Marunouchi",
            "nearby_attractions": ["Imperial Palace", "Ginza", "Tsukiji Market"]
        }
    ],
    "sydney": [
        {
            "id": "syd1",
            "name": "Harbor View Hotel",
            "address": "1 Circular Quay, Sydney NSW 2000",
            "stars": 5,
            "rating": 4.8,
            "reviews": 580,
            "description": "Luxury hotel with panoramic views of Sydney Harbor and the Opera House.",
            "price_per_night": 480,
            "room_types": ["Standard", "Deluxe", "Suite", "Presidential"],
            "amenities": ["pool", "breakfast", "parking", "wifi", "fitness", "spa", "restaurant", "bar", "conference"],
            "image_url": "https://images.unsplash.com/photo-1506973035872-a4ec16b8e8d9?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80",
            "highlights": ["Opera House View", "Infinity Pool", "Fine Dining"],
            "location": "Circular Quay",
            "nearby_attractions": ["Sydney Opera House", "Harbor Bridge", "Royal Botanic Garden"]
        }
    ],
    "dubai": [
        {
            "id": "dxb1",
            "name": "Burj Al Arab Hotel",
            "address": "Jumeirah Beach Road, Dubai, UAE",
            "stars": 7,
            "rating": 4.9,
            "reviews": 1200,
            "description": "Iconic luxury hotel shaped like a sail, offering unparalleled luxury and service.",
            "price_per_night": 1200,
            "room_types": ["Deluxe", "Suite", "Presidential", "Royal"],
            "amenities": ["pool", "breakfast", "parking", "wifi", "fitness", "spa", "restaurant", "bar", "conference", "helicopter"],
            "image_url": "https://images.unsplash.com/photo-1542314831-068cd1dbfeeb?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80",
            "highlights": ["Private Beach", "Helicopter Transfer", "Underwater Restaurant"],
            "location": "Jumeirah Beach",
            "nearby_attractions": ["Dubai Mall", "Palm Jumeirah", "Dubai Marina"]
        }
    ],
    "singapore": [
        {
            "id": "sgp1",
            "name": "Marina Bay Sands",
            "address": "10 Bayfront Avenue, Singapore 018956",
            "stars": 5,
            "rating": 4.8,
            "reviews": 1500,
            "description": "Luxury integrated resort featuring the world's largest rooftop infinity pool.",
            "price_per_night": 600,
            "room_types": ["Deluxe", "Suite", "Presidential"],
            "amenities": ["pool", "breakfast", "parking", "wifi", "fitness", "spa", "restaurant", "bar", "conference", "casino"],
            "image_url": "https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80",
            "highlights": ["Infinity Pool", "SkyPark", "ArtScience Museum"],
            "location": "Marina Bay",
            "nearby_attractions": ["Gardens by the Bay", "Singapore Flyer", "Merlion Park"]
        }
    ]
}

# Initialize hotel data provider
hotel_provider = HotelDataProvider()

class BookingRequest(BaseModel):
    hotel_id: str
    check_in: str
    check_out: str
    guests: int
    room_type: str
    name: str
    email: str
    phone: str
    destination: str
    adults: int
    children: int = 0
    preferences: Dict[str, bool] = {}

class BookingResponse(BaseModel):
    status: str
    hotels: List[Dict]

class SearchRequest(BaseModel):
    destination: str
    check_in: str
    check_out: str
    guests: int
    price_range: Optional[float] = None
    amenities: Optional[List[str]] = None

# Security configurations
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

# Generate a secure API key if not provided
if not os.getenv("API_KEY"):
    os.environ["API_KEY"] = secrets.token_urlsafe(32)
API_KEY = os.getenv("API_KEY")

async def get_api_key(api_key_header: str = Security(api_key_header)):
    if not api_key_header:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="Could not validate API key"
        )
    if api_key_header != API_KEY:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="Invalid API key"
        )
    return api_key_header

@app.route("/", methods=['GET'])
async def read_root():
    """Render the main page with improved error handling"""
    try:
        return render_template("index.html")
    except Exception as e:
        logger.error(f"Error rendering index.html: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route("/api/search", methods=['POST'])
async def search_hotels():
    """Search for hotels with improved security and validation"""
    try:
        data = request.get_json()
        # Sanitize and validate search parameters
        sanitized_params = sanitize_search_params(data)
        
        # Get hotels from Google Places API
        google_hotels = await hotel_provider.get_google_places_hotels(sanitized_params["destination"])
        
        # Get additional hotels from OpenStreetMap
        osm_hotels = await hotel_provider.get_osm_hotels(sanitized_params["destination"])
        
        # Combine and deduplicate hotels
        all_hotels = google_hotels + osm_hotels
        unique_hotels = {hotel['id']: hotel for hotel in all_hotels}.values()
        
        # Apply filters if provided
        hotels = list(unique_hotels)
        if sanitized_params.get("price_range"):
            hotels = [h for h in hotels if h["price_per_night"] <= sanitized_params["price_range"]]
        
        if sanitized_params.get("amenities"):
            hotels = [h for h in hotels if all(a in h["amenities"] for a in sanitized_params["amenities"])]
        
        # Log sanitized results
        logger.info(f"Found {len(hotels)} hotels matching criteria")
        if hotels:
            safe_hotel = sanitize_log_data(hotels[0])
            logger.info(f"Sample hotel: {safe_hotel['name']} in {safe_hotel['location']}")
        
        return jsonify({"hotels": hotels})
    except Exception as e:
        logger.error(f"Error searching hotels: {str(e)}")
        return jsonify({"error": "Failed to search hotels"}), 500

@app.route("/api/book", methods=['POST'])
async def book_hotel():
    """Book a hotel with enhanced security and validation"""
    try:
        data = request.get_json()
        # Validate hotel ID
        if not validate_hotel_id(data["hotel_id"]):
            return jsonify({"error": "Invalid hotel ID"}), 400
        
        # Generate secure booking reference
        booking_ref = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        
        # Log sanitized booking data
        safe_data = sanitize_log_data(data)
        logger.info(f"Processing booking: {safe_data}")
        
        return jsonify({
            "status": "success",
            "booking": {
                "reference": booking_ref,
                "hotel_id": data["hotel_id"],
                "check_in": data["check_in"],
                "check_out": data["check_out"],
                "guests": data["guests"],
                "room_type": data["room_type"],
                "name": data["name"],
                "email": data["email"],
                "phone": data["phone"],
                "destination": data["destination"],
                "adults": data["adults"],
                "children": data["children"],
                "preferences": data["preferences"]
            }
        })
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Error processing booking: {str(e)}")
        return jsonify({"error": "Failed to process booking"}), 500

@app.route("/api/amenities", methods=['GET'])
async def get_amenities():
    """Get list of available amenities"""
    return jsonify({
        "status": "success",
        "amenities": ui_agent.amenities
    })

@app.route("/api/room-types", methods=['GET'])
async def get_room_types():
    """Get list of available room types"""
    from app.hotel_booking_system_v2 import RoomType
    return jsonify({
        "status": "success",
        "room_types": [{"id": rt.name, "name": rt.value} for rt in RoomType]
    })

@app.route("/health", methods=['GET'])
async def health_check():
    return jsonify({"status": "healthy", "version": "2.1"})

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8000")),
        ssl_keyfile=os.getenv("SSL_KEYFILE"),
        ssl_certfile=os.getenv("SSL_CERTFILE")
    ) 