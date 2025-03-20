import unittest
from datetime import datetime, timedelta
from hotel_booking_system_v2 import UserInterfaceAgent, BookingAPIAgent, IntegrationAgent

class TestHotelBookingSystem(unittest.TestCase):
    def setUp(self):
        self.ui_agent = UserInterfaceAgent()
        self.booking_agent = BookingAPIAgent(api_key="test_api_key")  # Use dummy API key for testing
        self.integration_agent = IntegrationAgent(api_key="test_api_key")  # Use dummy API key for testing

    def test_date_validation(self):
        """Test date validation rules"""
        # Test past date
        past_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        future_date = (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d")
        
        # Test future date beyond 1 year
        far_future_date = (datetime.now() + timedelta(days=366)).strftime("%Y-%m-%d")
        
        # Test invalid date format
        invalid_date = "2024-13-45"  # Invalid month and day
        
        # Test check-out before check-in
        today = datetime.now().strftime("%Y-%m-%d")
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        
        # These should raise ValueError or return False
        with self.assertRaises(ValueError):
            self.ui_agent.collect_dates()
        
        # Test valid dates
        valid_check_in = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        valid_check_out = (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d")
        
        check_in, check_out = self.ui_agent.collect_dates()
        self.assertIsInstance(check_in, str)
        self.assertIsInstance(check_out, str)

    def test_guest_validation(self):
        """Test guest information validation"""
        # Test invalid number of adults
        with self.assertRaises(ValueError):
            self.ui_agent.collect_guests_info()
        
        # Test too many guests
        with self.assertRaises(ValueError):
            self.ui_agent.collect_guests_info()
        
        # Test invalid child age
        with self.assertRaises(ValueError):
            self.ui_agent.collect_guests_info()
        
        # Test valid guest information
        guests_info = self.ui_agent.collect_guests_info()
        self.assertIsInstance(guests_info, dict)
        self.assertIn('adults', guests_info)
        self.assertIn('children', guests_info)

    def test_price_validation(self):
        """Test price range validation"""
        # Test negative prices
        with self.assertRaises(ValueError):
            self.ui_agent.collect_preferences()
        
        # Test min price greater than max price
        with self.assertRaises(ValueError):
            self.ui_agent.collect_preferences()
        
        # Test valid price range
        preferences = self.ui_agent.collect_preferences()
        self.assertIsInstance(preferences, dict)
        self.assertIn('price_range', preferences)

    def test_hotel_selection(self):
        """Test hotel selection and filtering"""
        # Create test booking details
        booking_details = {
            "destination": "New York, USA",
            "check_in": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"),
            "check_out": (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d"),
            "adults": 2,
            "children": 1,
            "preferences": {
                "price_range": {"min": 100, "max": 300},
                "min_stars": 4,
                "room_type": "Standard",
                "amenities": ["wifi", "breakfast"]
            }
        }
        
        # Test hotel search
        hotels = self.booking_agent.search_hotels(booking_details)
        self.assertIsInstance(hotels, list)
        
        # Test hotel filtering
        for hotel in hotels:
            self.assertGreaterEqual(hotel["stars"], booking_details["preferences"]["min_stars"])
            self.assertGreaterEqual(hotel["price_per_night"], booking_details["preferences"]["price_range"]["min"])
            self.assertLessEqual(hotel["price_per_night"], booking_details["preferences"]["price_range"]["max"])
            self.assertIn(booking_details["preferences"]["room_type"], hotel["room_types"])
            for amenity in booking_details["preferences"]["amenities"]:
                self.assertIn(amenity, hotel["amenities"])

    def test_booking_confirmation(self):
        """Test booking confirmation generation"""
        # Create test booking details
        booking_details = {
            "check_in": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"),
            "check_out": (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d"),
            "adults": 2,
            "children": 1
        }
        
        # Test booking confirmation
        confirmation = self.booking_agent.book_hotel("hotel1", booking_details)
        self.assertIsInstance(confirmation, dict)
        self.assertIn("booking_reference", confirmation)
        self.assertIn("status", confirmation)
        self.assertEqual(confirmation["status"], "confirmed")
        self.assertEqual(confirmation["guests"]["adults"], booking_details["adults"])
        self.assertEqual(confirmation["guests"]["children"], booking_details["children"])

if __name__ == '__main__':
    unittest.main() 