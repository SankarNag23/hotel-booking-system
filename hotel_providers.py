import os
import logging
from typing import List, Dict, Optional
import googlemaps
from overpy import Overpass
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HotelDataProvider:
    def __init__(self):
        self.google_maps = googlemaps.Client(key=os.getenv('GOOGLE_PLACES_API_KEY'))
        self.overpass = Overpass()
        self.geocoder = Nominatim(user_agent="hotel_booking_system")
        
    async def get_coordinates(self, destination: str) -> Optional[tuple]:
        """Get coordinates for a destination using geopy"""
        try:
            location = self.geocoder.geocode(destination)
            if location:
                return (location.latitude, location.longitude)
            return None
        except GeocoderTimedOut:
            logger.error(f"Geocoding timeout for destination: {destination}")
            return None

    async def get_google_places_hotels(self, destination: str) -> List[Dict]:
        """Get hotel data from Google Places API"""
        try:
            # First, get the location coordinates
            coords = await self.get_coordinates(destination)
            if not coords:
                return []

            # Search for hotels near the location
            places_result = self.google_maps.places_nearby(
                location=coords,
                radius=5000,  # 5km radius
                type='lodging',
                language='en'
            )

            hotels = []
            for place in places_result.get('results', []):
                try:
                    # Get detailed information for each place
                    details = self.google_maps.place(place['place_id'], fields=[
                        'name', 'formatted_address', 'rating', 'reviews',
                        'photos', 'website', 'opening_hours', 'price_level',
                        'formatted_phone_number', 'international_phone_number',
                        'opening_hours', 'types', 'user_ratings_total'
                    ])

                    # Get photos
                    photo_url = self._get_photo_url(place.get('photos', []))
                    
                    # Get amenities from place types
                    amenities = self._get_amenities_from_types(details.get('types', []))
                    
                    # Get price level
                    price_level = details.get('price_level', 0)
                    price_per_night = self._estimate_price(price_level)
                    
                    # Get rating and reviews
                    rating = details.get('rating', 0)
                    reviews = details.get('user_ratings_total', 0)
                    
                    # Get opening hours
                    opening_hours = details.get('opening_hours', {})
                    is_24_7 = opening_hours.get('open_now', False)
                    
                    hotel = {
                        'id': place['place_id'],
                        'name': place['name'],
                        'address': place['vicinity'],
                        'stars': int(rating),  # Convert rating to stars
                        'rating': rating,
                        'reviews': reviews,
                        'description': f"Hotel located in {place['vicinity']}",
                        'price_per_night': price_per_night,
                        'room_types': self._get_room_types(price_level),
                        'amenities': amenities,
                        'image_url': photo_url,
                        'highlights': self._get_highlights(details),
                        'location': destination,
                        'nearby_attractions': await self._get_nearby_attractions(coords),
                        'phone': details.get('formatted_phone_number', ''),
                        'website': details.get('website', ''),
                        'is_24_7': is_24_7
                    }
                    hotels.append(hotel)
                    logger.info(f"Added hotel: {hotel['name']} with rating {rating}")
                    
                except Exception as e:
                    logger.error(f"Error processing hotel {place.get('name', 'Unknown')}: {str(e)}")
                    continue

            return hotels
        except Exception as e:
            logger.error(f"Error fetching Google Places data: {str(e)}")
            return []

    async def get_osm_hotels(self, destination: str) -> List[Dict]:
        """Get additional hotel data from OpenStreetMap"""
        try:
            coords = await self.get_coordinates(destination)
            if not coords:
                return []

            # Query OSM for hotels
            query = f"""
            [out:json][timeout:25];
            (
              node["tourism"="hotel"](around:5000,{coords[0]},{coords[1]});
              way["tourism"="hotel"](around:5000,{coords[0]},{coords[1]});
              relation["tourism"="hotel"](around:5000,{coords[0]},{coords[1]});
            );
            out body;
            >;
            out skel qt;
            """
            
            result = self.overpass.query(query)
            hotels = []

            for node in result.nodes:
                hotel = {
                    'id': f"osm_{node.id}",
                    'name': node.tags.get('name', 'Unnamed Hotel'),
                    'address': node.tags.get('addr:street', ''),
                    'stars': 0,  # OSM doesn't provide star ratings
                    'rating': 0,
                    'reviews': 0,
                    'description': f"Hotel located in {node.tags.get('addr:street', '')}",
                    'price_per_night': self._estimate_price_from_tags(node.tags),
                    'room_types': ['Standard', 'Deluxe', 'Suite'],
                    'amenities': self._get_amenities_from_tags(node.tags),
                    'image_url': node.tags.get('image', ''),
                    'highlights': self._get_highlights_from_tags(node.tags),
                    'location': destination,
                    'nearby_attractions': []
                }
                hotels.append(hotel)

            return hotels
        except Exception as e:
            logger.error(f"Error fetching OSM data: {str(e)}")
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