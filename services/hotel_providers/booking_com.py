"""
Booking.com API Integration
Uses the Booking.com Affiliate Partner API for hotel searches and bookings.
"""

import os
import aiohttp
from datetime import datetime
from typing import List, Dict, Any, Optional
from . import HotelProvider, NoPaymentFilter, FreeCancellationFilter

class BookingComProvider(HotelProvider, NoPaymentFilter, FreeCancellationFilter):
    """Booking.com API integration."""
    
    def __init__(self):
        self.api_key = os.environ.get('BOOKING_API_KEY')
        self.base_url = "https://distribution-xml.booking.com/2.0"
        
    async def _make_request(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Make authenticated request to Booking.com API."""
        headers = {
            "Authorization": f"Basic {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/{endpoint}", 
                                 headers=headers, 
                                 params=params) as response:
                return await response.json()
    
    async def search_hotels(self,
                          location: str,
                          check_in: datetime,
                          check_out: datetime,
                          guests: int,
                          filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Search for hotels on Booking.com."""
        params = {
            "city": location,
            "arrival_date": check_in.strftime("%Y-%m-%d"),
            "departure_date": check_out.strftime("%Y-%m-%d"),
            "guests": guests,
            "room_number": 1,
            "extras": "hotel_details,room_details,payment_details,cancellation_policy"
        }
        
        if filters:
            params.update(filters)
        
        try:
            results = await self._make_request("hotels", params)
            hotels = results.get("hotels", [])
            
            # Apply filters for no-payment and free cancellation if requested
            if filters and filters.get("no_payment_only"):
                for hotel in hotels:
                    hotel["rooms"] = self.filter_no_payment_options(hotel.get("rooms", []))
                    
            if filters and filters.get("free_cancellation_only"):
                for hotel in hotels:
                    hotel["rooms"] = self.filter_free_cancellation(hotel.get("rooms", []))
            
            # Remove hotels with no available rooms after filtering
            hotels = [hotel for hotel in hotels if hotel.get("rooms")]
            
            return hotels
            
        except Exception as e:
            print(f"Error searching Booking.com hotels: {str(e)}")
            return []
    
    async def get_room_availability(self,
                                  hotel_id: str,
                                  check_in: datetime,
                                  check_out: datetime,
                                  guests: int) -> List[Dict[str, Any]]:
        """Get available rooms for a specific hotel."""
        params = {
            "hotel_ids": hotel_id,
            "arrival_date": check_in.strftime("%Y-%m-%d"),
            "departure_date": check_out.strftime("%Y-%m-%d"),
            "guests": guests,
            "extras": "room_details,payment_details,cancellation_policy"
        }
        
        try:
            results = await self._make_request(f"hotels/{hotel_id}/rooms", params)
            return results.get("rooms", [])
        except Exception as e:
            print(f"Error getting room availability: {str(e)}")
            return []
    
    async def get_cancellation_policy(self,
                                    hotel_id: str,
                                    room_id: str) -> Dict[str, Any]:
        """Get cancellation policy for a specific room."""
        try:
            results = await self._make_request(
                f"hotels/{hotel_id}/rooms/{room_id}/policies",
                {}
            )
            return results.get("cancellation_policy", {})
        except Exception as e:
            print(f"Error getting cancellation policy: {str(e)}")
            return {} 