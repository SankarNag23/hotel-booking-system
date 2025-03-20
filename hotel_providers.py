import os
import json
import logging
import httpx
from typing import List, Dict, Any
import asyncio
from datetime import datetime, timedelta
from overpy import Overpass
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HotelDataProvider:
    def __init__(self):
        self.use_mock_data = os.getenv("USE_MOCK_DATA", "true").lower() == "true"
        self.mock_data = {
            "london": [{
                "id": "ld001",
                "name": "Royal Park Hotel",
                "location": "Hyde Park",
                "price_per_night": 500,
                "stars": 4.9,
                "reviews": 1250,
                "image_url": "/static/images/hotels/london-royal-park.jpg",
                "amenities": ["pool", "spa", "wifi", "breakfast"],
                "highlights": ["Hyde Park View", "Luxury Spa", "Fine Dining"],
                "nearby": ["Hyde Park", "Buckingham Palace"]
            }],
            "new york": [{
                "id": "ny001",
                "name": "Grand Central Hotel",
                "location": "Manhattan",
                "price_per_night": 450,
                "stars": 4.8,
                "reviews": 2100,
                "image_url": "/static/images/hotels/ny-grand-central.jpg",
                "amenities": ["gym", "restaurant", "wifi", "bar"],
                "highlights": ["Central Park View", "Fine Dining"],
                "nearby": ["Central Park", "Times Square"]
            },
            {
                "id": "ny002",
                "name": "Broadway Plaza Hotel",
                "location": "Theater District",
                "price_per_night": 380,
                "stars": 4.6,
                "reviews": 1800,
                "image_url": "/static/images/hotels/ny-broadway-plaza.jpg",
                "amenities": ["wifi", "restaurant", "bar"],
                "highlights": ["Theater District Location", "Rooftop Bar"],
                "nearby": ["Broadway", "Times Square"]
            }],
            "paris": [{
                "id": "pr001",
                "name": "Eiffel View Hotel",
                "location": "7th Arrondissement",
                "price_per_night": 400,
                "stars": 4.5,
                "reviews": 1500,
                "image_url": "/static/images/hotels/paris-eiffel.jpg",
                "amenities": ["breakfast", "wifi", "bar"],
                "highlights": ["Eiffel Tower View", "Rooftop Bar"],
                "nearby": ["Eiffel Tower", "Musée d'Orsay"]
            }]
        }
        self.google_maps = googlemaps.Client(key=os.getenv('GOOGLE_PLACES_API_KEY'))
        self.overpass = Overpass()
        self.geocoder = Nominatim(user_agent="hotel_booking_system")
        
    async def get_coordinates(self, destination: str) -> Any:
        """Get coordinates for a destination using geopy"""
        try:
            location = self.geocoder.geocode(destination)
            if location:
                return (location.latitude, location.longitude)
            return None
        except GeocoderTimedOut:
            logger.error(f"Geocoding timeout for destination: {destination}")
            return None

    async def get_google_places_hotels(self, destination: str) -> List[Dict[str, Any]]:
        """Fetch hotel data from Google Places API with fallback to mock data"""
        if self.use_mock_data:
            logger.info("Using mock data as configured")
            return self.get_mock_hotels(destination)

        try:
            api_key = os.getenv("GOOGLE_PLACES_API_KEY")
            client_id = os.getenv("GOOGLE_HOTELS_CLIENT_ID")
            
            if not api_key or not client_id:
                logger.warning("Missing API credentials, falling back to mock data")
                return self.get_mock_hotels(destination)

            async with httpx.AsyncClient() as client:
                # Get hotel content
                content_response = await client.get(
                    "https://hotels.googleapis.com/v1/hotelContent",
                    params={
                        "key": api_key,
                        "clientId": client_id,
                        "location": destination,
                        "languageCode": "en"
                    }
                )
                
                # Get hotel prices
                prices_response = await client.get(
                    "https://hotels.googleapis.com/v1/hotelPrices",
                    params={
                        "key": api_key,
                        "clientId": client_id,
                        "location": destination,
                        "checkIn": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"),
                        "checkOut": (datetime.now() + timedelta(days=35)).strftime("%Y-%m-%d")
                    }
                )

                if content_response.status_code != 200 or prices_response.status_code != 200:
                    logger.error(f"Failed to fetch hotel data. Content status: {content_response.status_code}, Prices status: {prices_response.status_code}")
                    return self.get_mock_hotels(destination)

                # Process and combine the responses
                content_data = content_response.json()
                prices_data = prices_response.json()
                
                # Transform the data to our format
                return self.transform_google_data(content_data, prices_data)
        except Exception as e:
            logger.error(f"Error fetching hotel data: {str(e)}")
            return self.get_mock_hotels(destination)

    def get_mock_hotels(self, destination: str) -> List[Dict[str, Any]]:
        """Get mock hotel data for a destination"""
        destination_lower = destination.lower()
        if destination_lower in self.mock_data:
            logger.info(f"Using mock data for {destination}")
            return self.mock_data[destination_lower]
        return []

    def transform_google_data(self, content_data: Dict[str, Any], prices_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Transform Google Hotels API data to our format"""
        hotels = []
        try:
            for hotel in content_data.get("hotels", []):
                hotel_id = hotel.get("id")
                price_info = next((p for p in prices_data.get("prices", []) if p.get("hotelId") == hotel_id), {})
                
                hotels.append({
                    "id": hotel_id,
                    "name": hotel.get("name", ""),
                    "location": hotel.get("location", {}).get("address", ""),
                    "price_per_night": price_info.get("price", {}).get("amount", 0),
                    "stars": hotel.get("rating", {}).get("overall", 0),
                    "reviews": hotel.get("reviewCount", 0),
                    "image_url": hotel.get("photos", [{}])[0].get("url", ""),
                    "amenities": [a.get("name") for a in hotel.get("amenities", [])],
                    "highlights": [h.get("text") for h in hotel.get("highlights", [])],
                    "nearby": [p.get("name") for p in hotel.get("nearbyPlaces", [])]
                })
        except Exception as e:
            logger.error(f"Error transforming hotel data: {str(e)}")
        
        return hotels

    async def get_osm_hotels(self, destination: str) -> List[Dict[str, Any]]:
        """This method can be implemented later for OpenStreetMap integration"""
        return []

    def _estimate_price(self, price_level: int) -> float:
        """Estimate price based on Google Places price level"""
        price_map = {
            0: 50,    # Free
            1: 100,   # Inexpensive
            2: 200,   # Moderate
            3: 300,   # Expensive
            4: 500    # Very Expensive
        }
        return price_map.get(price_level, 200)

    def _estimate_price_from_tags(self, tags: Dict) -> float:
        """Estimate price based on OSM tags"""
        if 'stars' in tags:
            return int(tags['stars']) * 100
        return 200

    def _get_amenities(self, details: Dict) -> List[str]:
        """Extract amenities from Google Places details"""
        amenities = []
        if details.get('opening_hours', {}).get('open_now'):
            amenities.append('24/7')
        if details.get('website'):
            amenities.append('wifi')
        return amenities

    def _get_amenities_from_tags(self, tags: Dict) -> List[str]:
        """Extract amenities from OSM tags"""
        amenities = []
        amenity_map = {
            'internet_access': 'wifi',
            'parking': 'parking',
            'pool': 'pool',
            'restaurant': 'restaurant',
            'bar': 'bar'
        }
        for key, value in amenity_map.items():
            if key in tags:
                amenities.append(value)
        return amenities

    def _get_photo_url(self, photos: List[Dict]) -> str:
        """Get photo URL from Google Places photos"""
        if photos:
            photo_reference = photos[0].get('photo_reference')
            if photo_reference:
                return f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=800&photo_reference={photo_reference}&key={os.getenv('GOOGLE_PLACES_API_KEY')}"
        return "https://images.unsplash.com/photo-1566073771259-6a8506099945?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80"

    def _get_highlights(self, details: Dict) -> List[str]:
        """Extract highlights from place details"""
        highlights = []
        
        # Add rating highlight
        if details.get('rating'):
            highlights.append(f"{details['rating']} Star Rating")
        
        # Add 24/7 highlight
        if details.get('opening_hours', {}).get('open_now'):
            highlights.append("Open 24/7")
        
        # Add price level highlight
        price_level = details.get('price_level', 0)
        if price_level >= 4:
            highlights.append("Luxury Hotel")
        elif price_level >= 3:
            highlights.append("Premium Hotel")
        
        return highlights

    def _get_highlights_from_tags(self, tags: Dict) -> List[str]:
        """Extract highlights from OSM tags"""
        highlights = []
        if 'stars' in tags:
            highlights.append(f"{tags['stars']} Star Rating")
        return highlights

    def _get_nearby_attractions(self, coords: tuple) -> List[str]:
        """Get nearby attractions using Google Places API"""
        try:
            places_result = self.google_maps.places_nearby(
                location=coords,
                radius=2000,  # 2km radius
                type='tourist_attraction',
                language='en'
            )
            return [place['name'] for place in places_result.get('results', [])[:3]]
        except Exception as e:
            logger.error(f"Error fetching nearby attractions: {str(e)}")
            return []

    def _get_amenities_from_types(self, types: List[str]) -> List[str]:
        """Extract amenities from place types"""
        amenities = []
        type_to_amenity = {
            'lodging': 'hotel',
            'restaurant': 'restaurant',
            'bar': 'bar',
            'gym': 'fitness',
            'parking': 'parking',
            'wifi': 'wifi',
            'pool': 'pool',
            'spa': 'spa'
        }
        
        for type_ in types:
            if type_ in type_to_amenity:
                amenities.append(type_to_amenity[type_])
        
        return list(set(amenities))  # Remove duplicates

    def _get_room_types(self, price_level: int) -> List[str]:
        """Get room types based on price level"""
        if price_level >= 4:
            return ['Standard', 'Deluxe', 'Suite', 'Presidential', 'Royal']
        elif price_level >= 3:
            return ['Standard', 'Deluxe', 'Suite']
        else:
            return ['Standard', 'Deluxe'] 