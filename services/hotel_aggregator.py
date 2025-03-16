"""
Hotel Aggregator Service
Combines and filters results from multiple hotel providers.
"""

import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional
from .hotel_providers import BookingComProvider, OpenTravelProvider

class HotelAggregator:
    """Aggregates hotel data from multiple providers."""
    
    def __init__(self):
        self.providers = [
            BookingComProvider(),
            OpenTravelProvider()
        ]
    
    async def search_hotels(self,
                          location: str,
                          check_in: datetime,
                          check_out: datetime,
                          guests: int,
                          filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Search hotels across all providers."""
        
        # Create tasks for each provider
        tasks = [
            provider.search_hotels(
                location=location,
                check_in=check_in,
                check_out=check_out,
                guests=guests,
                filters=filters
            )
            for provider in self.providers
        ]
        
        # Execute all searches concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Combine and process results
        all_hotels = []
        for provider_results in results:
            if isinstance(provider_results, list):  # Successful result
                all_hotels.extend(provider_results)
            else:  # Exception occurred
                print(f"Error from provider: {str(provider_results)}")
        
        # Apply global filters
        if filters:
            if filters.get("no_payment_only"):
                all_hotels = [
                    hotel for hotel in all_hotels
                    if not hotel.get("payment_required", True)
                ]
            
            if filters.get("free_cancellation_only"):
                all_hotels = [
                    hotel for hotel in all_hotels
                    if hotel.get("free_cancellation", False)
                ]
            
            if filters.get("min_price") is not None:
                all_hotels = [
                    hotel for hotel in all_hotels
                    if hotel.get("price", 0) >= filters["min_price"]
                ]
            
            if filters.get("max_price") is not None:
                all_hotels = [
                    hotel for hotel in all_hotels
                    if hotel.get("price", 0) <= filters["max_price"]
                ]
            
            if filters.get("min_rating") is not None:
                all_hotels = [
                    hotel for hotel in all_hotels
                    if hotel.get("rating", 0) >= filters["min_rating"]
                ]
        
        # Sort results
        sort_by = filters.get("sort_by", "price") if filters else "price"
        reverse = filters.get("sort_order", "asc") == "desc" if filters else False
        
        all_hotels.sort(
            key=lambda x: (
                x.get(sort_by, 0) if sort_by != "rating" 
                else x.get(sort_by, 0) * -1  # Higher ratings first
            ),
            reverse=reverse
        )
        
        return {
            "total": len(all_hotels),
            "hotels": all_hotels,
            "filters_applied": filters or {},
            "sources": [
                "Booking.com",
                "OpenStreetMap",
                "Wikivoyage"
            ]
        }
    
    async def get_hotel_details(self,
                              hotel_id: str,
                              check_in: datetime,
                              check_out: datetime,
                              guests: int) -> Dict[str, Any]:
        """Get detailed information about a specific hotel."""
        tasks = [
            provider.get_room_availability(
                hotel_id=hotel_id,
                check_in=check_in,
                check_out=check_out,
                guests=guests
            )
            for provider in self.providers
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Combine room availability from all providers
        all_rooms = []
        for provider_rooms in results:
            if isinstance(provider_rooms, list):
                all_rooms.extend(provider_rooms)
        
        return {
            "hotel_id": hotel_id,
            "rooms": all_rooms,
            "total_rooms": len(all_rooms)
        }
    
    def format_hotel_response(self, hotels: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format hotel data for API response."""
        return [
            {
                "id": hotel.get("id"),
                "name": hotel.get("name"),
                "source": hotel.get("source", "Unknown"),
                "price": hotel.get("price", 0),
                "rating": hotel.get("rating"),
                "address": hotel.get("address"),
                "image": hotel.get("image"),
                "free_cancellation": hotel.get("free_cancellation", False),
                "payment_required": hotel.get("payment_required", True),
                "rooms_available": hotel.get("rooms_available", 0)
            }
            for hotel in hotels
        ] 