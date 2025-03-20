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
from .hotel_booking_system_v2 import UserInterfaceAgent, BookingAPIAgent, IntegrationAgent
from dotenv import load_dotenv
from .hotel_providers import HotelDataProvider
from .middleware import (
    SecurityHeadersMiddleware,
    RequestLoggingMiddleware,
    RateLimitMiddleware,
    SQLInjectionMiddleware,
    XSSMiddleware
)
from .validators import (
    BookingRequest,
    sanitize_search_params,
    validate_api_key,
    validate_hotel_id,
    sanitize_log_data
)
from fastapi.security import APIKeyHeader
from fastapi.security.api_key import APIKey
from starlette.status import HTTP_403_FORBIDDEN
import secrets
import re
import json
from fastapi.middleware import Middleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

# Configure logging with more detailed format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Get API keys from environment variables with validation
BOOKING_API_KEY = os.getenv("BOOKING_API_KEY")
GOOGLE_HOTELS_API_KEY = os.getenv("GOOGLE_HOTELS_API_KEY")
GOOGLE_HOTELS_CLIENT_ID = os.getenv("GOOGLE_HOTELS_CLIENT_ID")

if not validate_api_key(BOOKING_API_KEY):
    logger.error("Invalid or missing BOOKING_API_KEY")
    raise ValueError("Invalid or missing BOOKING_API_KEY")

# Check if Google Hotels API credentials are available
GOOGLE_HOTELS_AVAILABLE = bool(GOOGLE_HOTELS_API_KEY and GOOGLE_HOTELS_CLIENT_ID)

app = FastAPI(
    title="Hotel Booking System API",
    description="API for the Automated Hotel Booking System V2.1",
    version="2.1.0",
    docs_url="/api/docs",  # Restrict Swagger UI access
    redoc_url="/api/redoc"  # Restrict ReDoc access
)

# Add security middlewares
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(RateLimitMiddleware, max_requests=100, window_seconds=60)
app.add_middleware(SQLInjectionMiddleware)
app.add_middleware(XSSMiddleware)

# Configure CORS with specific origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("ALLOWED_ORIGINS", "http://localhost:8000")],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
    max_age=600
)

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
    # Mount static files
    app.mount("/static", StaticFiles(directory=static_dir, html=True), name="static")
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

# Rate limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": "Too many requests, please try again later."}
    )

async def get_google_hotels(destination: str, check_in: str, check_out: str) -> List[dict]:
    """Fetch hotel data from Google Hotels API with improved error handling"""
    if not GOOGLE_HOTELS_AVAILABLE:
        logger.warning("Google Hotels API credentials not available. Using mock data.")
        return []
        
    try:
        async with httpx.AsyncClient() as client:
            # Get hotel content
            content_response = await client.get(
                f"{GOOGLE_HOTELS_CONTENT_URL}",
                params={
                    "key": GOOGLE_HOTELS_API_KEY,
                    "clientId": GOOGLE_HOTELS_CLIENT_ID,
                    "location": destination,
                    "languageCode": "en"
                }
            )
            
            # Get hotel prices
            prices_response = await client.get(
                f"{GOOGLE_HOTELS_PRICES_URL}",
                params={
                    "key": GOOGLE_HOTELS_API_KEY,
                    "clientId": GOOGLE_HOTELS_CLIENT_ID,
                    "location": destination,
                    "checkIn": check_in,
                    "checkOut": check_out
                }
            )
            
            if content_response.status_code == 200 and prices_response.status_code == 200:
                content_data = content_response.json()
                prices_data = prices_response.json()
                
                # Combine and format the data
                hotels = []
                for hotel in content_data.get("hotels", []):
                    hotel_id = hotel.get("id")
                    price_info = next(
                        (p for p in prices_data.get("prices", []) if p.get("hotelId") == hotel_id),
                        {}
                    )
                    
                    hotels.append({
                        "id": hotel_id,
                        "name": hotel.get("name"),
                        "address": hotel.get("address"),
                        "stars": hotel.get("starRating", 0),
                        "rating": hotel.get("rating", 0),
                        "reviews": hotel.get("reviewCount", 0),
                        "description": hotel.get("description", ""),
                        "price_per_night": price_info.get("price", {}).get("amount", 0),
                        "room_types": hotel.get("roomTypes", []),
                        "amenities": hotel.get("amenities", []),
                        "image_url": hotel.get("images", [{}])[0].get("url", ""),
                        "highlights": hotel.get("highlights", []),
                        "location": hotel.get("location", {}).get("address", ""),
                        "nearby_attractions": hotel.get("nearbyAttractions", [])
                    })
                
                logger.info(f"Successfully fetched {len(hotels)} hotels from Google Hotels API")
                return hotels
            else:
                logger.error(f"Failed to fetch hotel data. Content status: {content_response.status_code}, Prices status: {prices_response.status_code}")
                return []
    except Exception as e:
        logger.error(f"Error fetching hotel data from Google Hotels API: {str(e)}")
        return []

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Render the main page with improved error handling"""
    try:
        return templates.TemplateResponse("index.html", {"request": request})
    except Exception as e:
        logger.error(f"Error rendering index.html: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/api/search")
@limiter.limit("30/minute")
async def search_hotels(request: Request, search_params: Dict):
    """Search for hotels with improved security and validation"""
    try:
        # Sanitize and validate search parameters
        sanitized_params = sanitize_search_params(search_params)
        
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
        
        return {"hotels": hotels}
    except Exception as e:
        logger.error(f"Error searching hotels: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to search hotels")

@app.post("/api/book")
@limiter.limit("5/minute")
async def book_hotel(request: BookingRequest):
    """Book a hotel with enhanced security and validation"""
    try:
        # Validate hotel ID
        if not validate_hotel_id(request.hotel_id):
            raise HTTPException(status_code=400, detail="Invalid hotel ID")
        
        # Generate secure booking reference
        booking_ref = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        
        # Log sanitized booking data
        safe_data = sanitize_log_data(request.dict())
        logger.info(f"Processing booking: {safe_data}")
        
        return {
            "status": "success",
            "booking": {
                "reference": booking_ref,
                "hotel_id": request.hotel_id,
                "check_in": request.check_in,
                "check_out": request.check_out,
                "guests": request.guests,
                "room_type": request.room_type,
                "name": request.name,
                "email": request.email,
                "phone": request.phone,
                "destination": request.destination,
                "adults": request.adults,
                "children": request.children,
                "preferences": request.preferences
            }
        }
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error processing booking: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to process booking")

@app.get("/api/amenities")
async def get_amenities():
    """Get list of available amenities"""
    return {
        "status": "success",
        "amenities": ui_agent.amenities
    }

@app.get("/api/room-types")
async def get_room_types():
    """Get list of available room types"""
    from .hotel_booking_system_v2 import RoomType
    return {
        "status": "success",
        "room_types": [{"id": rt.name, "name": rt.value} for rt in RoomType]
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "2.1"}

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8000")),
        ssl_keyfile=os.getenv("SSL_KEYFILE"),
        ssl_certfile=os.getenv("SSL_CERTFILE")
    ) 