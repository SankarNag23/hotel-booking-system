import asyncio
import httpx
import json
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_hotel_search():
    """Test the hotel search functionality"""
    # Test cases
    test_cases = [
        {
            "destination": "London",
            "check_in": "2025-04-22",
            "check_out": "2025-04-27",
            "guests": 1
        },
        {
            "destination": "New York",
            "check_in": "2025-05-01",
            "check_out": "2025-05-05",
            "guests": 2
        },
        {
            "destination": "Paris",
            "check_in": "2025-06-15",
            "check_out": "2025-06-20",
            "guests": 1
        }
    ]

    async with httpx.AsyncClient() as client:
        for test_case in test_cases:
            logger.info(f"\nTesting search for {test_case['destination']}")
            
            try:
                # Make the API request
                response = await client.post(
                    "http://localhost:8000/api/search",
                    json=test_case
                )
                
                if response.status_code == 200:
                    data = response.json()
                    hotels = data.get("hotels", [])
                    
                    # Log results
                    logger.info(f"Found {len(hotels)} hotels")
                    
                    if hotels:
                        # Log details of the first hotel
                        hotel = hotels[0]
                        logger.info("\nSample Hotel Details:")
                        logger.info(f"Name: {hotel.get('name')}")
                        logger.info(f"Location: {hotel.get('location')}")
                        logger.info(f"Price per night: ${hotel.get('price_per_night')}")
                        logger.info(f"Rating: {hotel.get('rating')} stars")
                        logger.info(f"Reviews: {hotel.get('reviews')}")
                        logger.info(f"Amenities: {', '.join(hotel.get('amenities', []))}")
                        logger.info(f"Highlights: {', '.join(hotel.get('highlights', []))}")
                        logger.info(f"Nearby attractions: {', '.join(hotel.get('nearby_attractions', []))}")
                    else:
                        logger.warning("No hotels found")
                else:
                    logger.error(f"Error: {response.status_code}")
                    logger.error(response.text)
                    
            except Exception as e:
                logger.error(f"Error testing {test_case['destination']}: {str(e)}")

async def test_booking():
    """Test the booking functionality"""
    test_case = {
        "hotel_id": "test_hotel_1",
        "check_in": "2025-04-22",
        "check_out": "2025-04-27",
        "guests": 1,
        "room_type": "Standard",
        "name": "John Doe",
        "email": "john@example.com",
        "phone": "+1234567890",
        "destination": "London",
        "adults": 1,
        "children": 0,
        "preferences": {"wifi": True, "breakfast": True}
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "http://localhost:8000/api/book",
                json=test_case
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info("\nBooking Test Results:")
                logger.info(f"Status: {data.get('status')}")
                logger.info(f"Booking Reference: {data.get('booking', {}).get('reference')}")
                logger.info(f"Hotel ID: {data.get('booking', {}).get('hotel_id')}")
                logger.info(f"Guest Name: {data.get('booking', {}).get('name')}")
                logger.info(f"Check-in: {data.get('booking', {}).get('check_in')}")
                logger.info(f"Check-out: {data.get('booking', {}).get('check_out')}")
            else:
                logger.error(f"Booking Error: {response.status_code}")
                logger.error(response.text)
                
        except Exception as e:
            logger.error(f"Error testing booking: {str(e)}")

async def main():
    """Run all tests"""
    logger.info("Starting hotel booking system tests...")
    
    # Test hotel search
    await test_hotel_search()
    
    # Test booking
    await test_booking()
    
    logger.info("\nTests completed!")

if __name__ == "__main__":
    asyncio.run(main()) 