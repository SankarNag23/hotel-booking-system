"""
Hotel Booking System
Version: 2.1.0
"""

from .app import app
from .hotel_booking_system_v2 import UserInterfaceAgent, BookingAPIAgent, IntegrationAgent, RoomType
from .hotel_providers import HotelDataProvider
from .middleware import SecurityHeadersMiddleware, RequestLoggingMiddleware, RateLimitMiddleware, SQLInjectionMiddleware, XSSMiddleware
from .validators import BookingRequest, sanitize_search_params, validate_api_key, validate_hotel_id, sanitize_log_data

__version__ = "2.1.0"
__all__ = ['app']
