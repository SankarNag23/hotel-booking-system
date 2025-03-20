from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
from hotel_booking_system_v2 import UserInterfaceAgent, BookingAPIAgent, IntegrationAgent

app = FastAPI(
    title="Hotel Booking System API",
    description="API for the Automated Hotel Booking System V2",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize agents
ui_agent = UserInterfaceAgent()
booking_agent = BookingAPIAgent(api_key="test_api_key")  # Use environment variable in production
integration_agent = IntegrationAgent(api_key="test_api_key")

class BookingRequest(BaseModel):
    destination: str
    check_in: str
    check_out: str
    adults: int
    children: int
    children_ages: Optional[List[int]] = None
    preferences: Dict[str, Any]

@app.get("/")
async def root():
    """Welcome endpoint"""
    return {
        "message": "Welcome to the Hotel Booking System API",
        "version": "2.0.0",
        "status": "operational"
    }

@app.post("/api/search")
async def search_hotels(booking_request: BookingRequest):
    """Search for hotels based on booking details"""
    try:
        # Convert request to booking details format
        booking_details = booking_request.dict()
        
        # Search for hotels
        hotels = booking_agent.search_hotels(booking_details)
        
        return {
            "status": "success",
            "hotels": hotels
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/book")
async def book_hotel(hotel_id: str, booking_request: BookingRequest):
    """Book a specific hotel"""
    try:
        # Convert request to booking details format
        booking_details = booking_request.dict()
        
        # Book the hotel
        confirmation = booking_agent.book_hotel(hotel_id, booking_details)
        
        return {
            "status": "success",
            "confirmation": confirmation
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

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
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 