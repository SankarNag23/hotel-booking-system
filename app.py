from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import uvicorn
import os
from datetime import datetime, timedelta
import random
import string
from hotel_booking_system_v2 import UserInterfaceAgent, BookingAPIAgent, IntegrationAgent

# Get API key from environment variable
API_KEY = os.getenv("BOOKING_API_KEY", "test_api_key")

app = FastAPI(
    title="Hotel Booking System API",
    description="API for the Automated Hotel Booking System V2",
    version="2.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files with explicit directory path
app.mount("/static", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "static")), name="static")

# Templates with explicit directory path
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "templates"))

# Initialize agents
ui_agent = UserInterfaceAgent()
booking_agent = BookingAPIAgent(api_key=API_KEY)
integration_agent = IntegrationAgent(api_key=API_KEY)

# Mock hotel database
HOTELS = {
    "new_york": [
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
            "image_url": "https://images.unsplash.com/photo-1542314831-068cd1dbfeeb?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80"
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
            "image_url": "https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80"
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
            "image_url": "https://images.unsplash.com/photo-1566073771259-6a8506099945?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80"
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
            "image_url": "https://images.unsplash.com/photo-1502602898657-3e91760cbb34?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80"
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
            "image_url": "https://images.unsplash.com/photo-1542051841857-5f90071e7989?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80"
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
            "image_url": "https://images.unsplash.com/photo-1506973035872-a4ec16b8e8d9?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80"
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

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    try:
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "title": "Hotel Booking System",
                "version": "2.0.0"
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error loading template: {str(e)}"
        )

@app.post("/api/search", response_model=BookingResponse)
async def search_hotels(booking_request: BookingRequest):
    try:
        # Convert destination to lowercase for matching
        destination = booking_request.destination.lower()
        
        # Get hotels for the destination
        available_hotels = HOTELS.get(destination, [])
        
        # Filter hotels based on preferences
        filtered_hotels = []
        for hotel in available_hotels:
            # Check price range
            if not (booking_request.preferences["price_range"]["min"] <= hotel["price_per_night"] <= booking_request.preferences["price_range"]["max"]):
                continue
                
            # Check minimum stars
            if hotel["stars"] < booking_request.preferences["min_stars"]:
                continue
                
            # Check room type
            if booking_request.preferences["room_type"] not in hotel["room_types"]:
                continue
                
            # Check amenities
            if not all(amenity in hotel["amenities"] for amenity in booking_request.preferences["amenities"]):
                continue
                
            filtered_hotels.append(hotel)
        
        return BookingResponse(
            status="success",
            hotels=filtered_hotels
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/book")
async def book_hotel(hotel_id: str, booking_request: BookingRequest):
    try:
        # Generate a random booking reference
        booking_reference = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        
        # In a real application, you would:
        # 1. Check hotel availability
        # 2. Process payment
        # 3. Create booking record in database
        # 4. Send confirmation email
        
        return {
            "status": "success",
            "confirmation": {
                "booking_reference": booking_reference,
                "hotel_id": hotel_id,
                "check_in": booking_request.check_in,
                "check_out": booking_request.check_out,
                "guests": {
                    "adults": booking_request.adults,
                    "children": booking_request.children
                }
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True) 