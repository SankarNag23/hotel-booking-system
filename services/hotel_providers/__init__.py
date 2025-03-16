"""
Hotel Providers Integration Module
This module handles integration with various hotel booking providers and APIs.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime

class HotelProvider(ABC):
    """Base class for hotel providers integration."""
    
    @abstractmethod
    async def search_hotels(self, 
                          location: str,
                          check_in: datetime,
                          check_out: datetime,
                          guests: int,
                          filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Search for hotels using the provider's API."""
        pass
    
    @abstractmethod
    async def get_room_availability(self,
                                  hotel_id: str,
                                  check_in: datetime,
                                  check_out: datetime,
                                  guests: int) -> List[Dict[str, Any]]:
        """Get available rooms for a specific hotel."""
        pass
    
    @abstractmethod
    async def get_cancellation_policy(self,
                                    hotel_id: str,
                                    room_id: str) -> Dict[str, Any]:
        """Get cancellation policy for a specific room."""
        pass

class NoPaymentFilter:
    """Mixin for filtering no-payment booking options."""
    
    def filter_no_payment_options(self, rooms: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter rooms that don't require payment."""
        return [
            room for room in rooms
            if room.get('payment_required', True) is False
            or room.get('total_price', 0) == 0
        ]

class FreeCancellationFilter:
    """Mixin for filtering free cancellation options."""
    
    def filter_free_cancellation(self, rooms: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter rooms with free cancellation."""
        return [
            room for room in rooms
            if room.get('free_cancellation', False) is True
            or room.get('cancellation_fee', 0) == 0
        ] 