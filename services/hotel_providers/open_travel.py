"""
OpenTravel Integration
Uses open-source hotel data and APIs to provide free hotel information.
"""

import aiohttp
from datetime import datetime
from typing import List, Dict, Any, Optional
from . import HotelProvider, NoPaymentFilter, FreeCancellationFilter

class OpenTravelProvider(HotelProvider, NoPaymentFilter, FreeCancellationFilter):
    """Integration with open-source hotel data providers."""
    
    def __init__(self):
        # Using Open Hotel Initiative API (example)
        self.base_url = "https://api.openhotels.org/v1"
        
        # Additional open data sources
        self.data_sources = [
            "https://api.openstreetmap.org/api/0.6",  # OpenStreetMap for hotel locations
            "https://api.wikivoyage.org/w/api.php",   # Wikivoyage for hotel information
        ]
    
    async def _fetch_osm_hotels(self, location: str) -> List[Dict[str, Any]]:
        """Fetch hotel data from OpenStreetMap."""
        query = f"""
        [out:json];
        area[name="{location}"]->.searchArea;
        (
          node["tourism"="hotel"](area.searchArea);
          way["tourism"="hotel"](area.searchArea);
          relation["tourism"="hotel"](area.searchArea);
        );
        out body;
        """
        
        async with aiohttp.ClientSession() as session:
            async with session.get("https://overpass-api.de/api/interpreter", 
                                 params={"data": query}) as response:
                data = await response.json()
                return [
                    {
                        "id": element["id"],
                        "name": element.get("tags", {}).get("name", "Unknown Hotel"),
                        "address": element.get("tags", {}).get("addr:full", ""),
                        "stars": element.get("tags", {}).get("stars", ""),
                        "website": element.get("tags", {}).get("website", ""),
                        "source": "OpenStreetMap"
                    }
                    for element in data.get("elements", [])
                ]
    
    async def _fetch_wiki_hotels(self, location: str) -> List[Dict[str, Any]]:
        """Fetch hotel information from Wikivoyage."""
        params = {
            "action": "query",
            "format": "json",
            "prop": "extracts",
            "titles": f"{location}/Sleep",
            "exintro": True
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get("https://en.wikivoyage.org/w/api.php",
                                 params=params) as response:
                data = await response.json()
                # Process and extract hotel information from wiki text
                # This is a simplified version
                return []
    
    async def search_hotels(self,
                          location: str,
                          check_in: datetime,
                          check_out: datetime,
                          guests: int,
                          filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Search for hotels using open data sources."""
        hotels = []
        
        # Fetch hotels from OpenStreetMap
        osm_hotels = await self._fetch_osm_hotels(location)
        hotels.extend(osm_hotels)
        
        # Fetch hotels from Wikivoyage
        wiki_hotels = await self._fetch_wiki_hotels(location)
        hotels.extend(wiki_hotels)
        
        # Apply filters
        if filters:
            if filters.get("no_payment_only"):
                hotels = self.filter_no_payment_options(hotels)
            if filters.get("free_cancellation_only"):
                hotels = self.filter_free_cancellation(hotels)
        
        return hotels
    
    async def get_room_availability(self,
                                  hotel_id: str,
                                  check_in: datetime,
                                  check_out: datetime,
                                  guests: int) -> List[Dict[str, Any]]:
        """Get room availability from open data."""
        # For open-source data, we'll return basic room types
        return [
            {
                "id": "standard",
                "name": "Standard Room",
                "capacity": 2,
                "price": 0,  # Free or contact hotel
                "payment_required": False,
                "free_cancellation": True
            },
            {
                "id": "family",
                "name": "Family Room",
                "capacity": 4,
                "price": 0,  # Free or contact hotel
                "payment_required": False,
                "free_cancellation": True
            }
        ]
    
    async def get_cancellation_policy(self,
                                    hotel_id: str,
                                    room_id: str) -> Dict[str, Any]:
        """Get cancellation policy."""
        # For open-source hotels, we assume flexible cancellation
        return {
            "free_cancellation": True,
            "cancellation_fee": 0,
            "deadline_days": 1,
            "notes": "Please contact the hotel directly for specific cancellation policies."
        } 