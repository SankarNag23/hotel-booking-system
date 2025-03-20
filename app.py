from fastapi import FastAPI, Request, HTTPException
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
from hotel_booking_system_v2 import UserInterfaceAgent, BookingAPIAgent, IntegrationAgent
from dotenv import load_dotenv

# Configure logging with more detailed format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Get API keys from environment variables
BOOKING_API_KEY = os.getenv("BOOKING_API_KEY", "test_api_key_123456789")
GOOGLE_HOTELS_API_KEY = os.getenv("GOOGLE_HOTELS_API_KEY")
GOOGLE_HOTELS_CLIENT_ID = os.getenv("GOOGLE_HOTELS_CLIENT_ID")

# Check if Google Hotels API credentials are available
GOOGLE_HOTELS_AVAILABLE = bool(GOOGLE_HOTELS_API_KEY and GOOGLE_HOTELS_CLIENT_ID)

app = FastAPI(
    title="Hotel Booking System API",
    description="API for the Automated Hotel Booking System V2.1",
    version="2.1.0"
)

# Configure CORS with specific origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get absolute paths for static files and templates
try:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    static_dir = os.path.join(current_dir, "static")
    templates_dir = os.path.join(current_dir, "templates")

    # Ensure directories exist
    os.makedirs(static_dir, exist_ok=True)
    os.makedirs(templates_dir, exist_ok=True)

    # Mount static files with absolute path
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

    # Templates with absolute path
    templates = Jinja2Templates(directory=templates_dir)
    
    logger.info(f"Static directory: {static_dir}")
    logger.info(f"Templates directory: {templates_dir}")
except Exception as e:
    logger.error(f"Error setting up directories: {str(e)}")
    raise

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

class BookingRequest(BaseModel):
    destination: str
    check_in: str
    check_out: str
    adults: int
    children: int
    preferences: Dict

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
async def search_hotels(request: SearchRequest):
    """Search for hotels with improved error handling and logging"""
    try:
        logger.info(f"Searching hotels for destination: {request.destination}")
        
        # Normalize destination for case-insensitive matching
        destination_key = request.destination.lower().strip()
        
        # Get hotels from Google Hotels API
        hotels = await get_google_hotels(request.destination, request.check_in, request.check_out)
        
        # If no hotels found from API, use mock data
        if not hotels:
            logger.info("Using mock data for hotel search")
            hotels = HOTELS.get(destination_key, [])
            
            # If still no hotels found, try partial matching
            if not hotels:
                for key in HOTELS.keys():
                    if destination_key in key or key in destination_key:
                        hotels.extend(HOTELS[key])
                        logger.info(f"Found hotels for partial match: {key}")
        
        # Apply filters if provided
        if request.price_range:
            hotels = [h for h in hotels if h["price_per_night"] <= request.price_range]
        
        if request.amenities:
            hotels = [h for h in hotels if all(a in h["amenities"] for a in request.amenities)]
        
        # Add more detailed logging
        logger.info(f"Found {len(hotels)} hotels matching criteria")
        if hotels:
            logger.info(f"Sample hotel: {hotels[0]['name']} in {hotels[0]['location']}")
        else:
            logger.warning("No hotels found matching the criteria")
        
        return {"hotels": hotels}
    except Exception as e:
        logger.error(f"Error searching hotels: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to search hotels")

@app.post("/api/book")
async def book_hotel(request: BookingRequest):
    """Book a hotel with improved error handling and validation"""
    try:
        # Validate dates
        check_in = datetime.strptime(request.check_in, "%Y-%m-%d").date()
        check_out = datetime.strptime(request.check_out, "%Y-%m-%d").date()
        
        if check_in >= check_out:
            raise HTTPException(status_code=400, detail="Check-out date must be after check-in date")
        
        # Generate booking reference
        booking_ref = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        
        # In a real implementation, this would create a booking in a database
        booking = {
            "reference": booking_ref,
            "hotel": request.destination,
            "check_in": request.check_in,
            "check_out": request.check_out,
            "adults": request.adults,
            "children": request.children,
            "preferences": request.preferences,
            "status": "confirmed",
            "created_at": datetime.now().isoformat()
        }
        
        logger.info(f"Booking created with reference: {booking_ref}")
        return {"status": "success", "booking": booking}
    except ValueError as e:
        logger.error(f"Invalid date format: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid date format")
    except Exception as e:
        logger.error(f"Error creating booking: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create booking")

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
    from hotel_booking_system_v2 import RoomType
    return {
        "status": "success",
        "room_types": [{"id": rt.name, "name": rt.value} for rt in RoomType]
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 