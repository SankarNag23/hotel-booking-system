import unittest
import requests
from datetime import datetime, timedelta

class TestHotelBookingAPI(unittest.TestCase):
    def setUp(self):
        self.base_url = "http://localhost:8000"  # Change this to your deployed URL
        self.test_booking_request = {
            "destination": "New York, USA",
            "check_in": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"),
            "check_out": (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d"),
            "adults": 2,
            "children": 1,
            "children_ages": [5],
            "preferences": {
                "price_range": {"min": 100, "max": 300},
                "min_stars": 4,
                "room_type": "Standard",
                "amenities": ["wifi", "breakfast"]
            }
        }

    def test_root_endpoint(self):
        """Test the root endpoint"""
        response = requests.get(f"{self.base_url}/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("message", data)
        self.assertIn("version", data)
        self.assertIn("status", data)

    def test_amenities_endpoint(self):
        """Test the amenities endpoint"""
        response = requests.get(f"{self.base_url}/api/amenities")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("status", data)
        self.assertIn("amenities", data)

    def test_room_types_endpoint(self):
        """Test the room types endpoint"""
        response = requests.get(f"{self.base_url}/api/room-types")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("status", data)
        self.assertIn("room_types", data)

    def test_search_endpoint(self):
        """Test the search endpoint"""
        response = requests.post(
            f"{self.base_url}/api/search",
            json=self.test_booking_request
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("status", data)
        self.assertIn("hotels", data)
        self.assertIsInstance(data["hotels"], list)

    def test_book_endpoint(self):
        """Test the book endpoint"""
        # First search for hotels
        search_response = requests.post(
            f"{self.base_url}/api/search",
            json=self.test_booking_request
        )
        hotels = search_response.json()["hotels"]
        
        if hotels:
            hotel_id = hotels[0]["id"]
            response = requests.post(
                f"{self.base_url}/api/book?hotel_id={hotel_id}",
                json=self.test_booking_request
            )
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertIn("status", data)
            self.assertIn("confirmation", data)
            self.assertEqual(data["confirmation"]["status"], "confirmed")

    def test_invalid_booking_request(self):
        """Test invalid booking request"""
        invalid_request = self.test_booking_request.copy()
        invalid_request["adults"] = -1  # Invalid number of adults
        
        response = requests.post(
            f"{self.base_url}/api/search",
            json=invalid_request
        )
        self.assertEqual(response.status_code, 400)

if __name__ == '__main__':
    unittest.main() 