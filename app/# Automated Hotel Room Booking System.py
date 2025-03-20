# Automated Hotel Room Booking System

import os
import json
import datetime
from typing import List, Dict, Any, Optional

# Agent1: User Interface for collecting booking details
class UserInterfaceAgent:
    def __init__(self):
        self.booking_details = {}
    
    def display_welcome_message(self):
        """Display a colorful welcome message to the user."""
        print("\n" + "="*50)
        print("🏨 Welcome to the Automated Hotel Booking System! 🏨")
        print("="*50 + "\n")
    
    def collect_destination(self) -> str:
        """Collect destination information from the user."""
        destination = input("📍 Enter your destination (city, country): ")
        self.booking_details["destination"] = destination
        return destination
    
    def collect_dates(self) -> tuple:
        """Collect check-in and check-out dates from the user."""
        while True:
            try:
                check_in_str = input("📅 Enter check-in date (YYYY-MM-DD): ")
                check_out_str = input("📅 Enter check-out date (YYYY-MM-DD): ")
                
                check_in = datetime.datetime.strptime(check_in_str, "%Y-%m-%d").date()
                check_out = datetime.datetime.strptime(check_out_str, "%Y-%m-%d").date()
                
                if check_out <= check_in:
                    print("❌ Check-out date must be after check-in date. Please try again.")
                    continue
                
                self.booking_details["check_in"] = check_in_str
                self.booking_details["check_out"] = check_out_str
                return check_in_str, check_out_str
            except ValueError:
                print("❌ Invalid date format. Please use YYYY-MM-DD format.")
    
    def collect_guests_info(self) -> Dict[str, int]:
        """Collect information about the number of adults and children."""
        while True:
            try:
                adults = int(input("👨‍👩‍👧‍👦 Number of adults: "))
                children = int(input("👶 Number of children: "))
                
                if adults < 1:
                    print("❌ There must be at least 1 adult. Please try again.")
                    continue
                
                if adults + children > 10:
                    print("❌ Maximum number of guests exceeded. Please try again.")
                    continue
                
                self.booking_details["adults"] = adults
                self.booking_details["children"] = children
                
                # If there are children, collect their ages
                children_ages = []
                for i in range(children):
                    age = int(input(f"👶 Age of child {i+1}: "))
                    children_ages.append(age)
                
                if children > 0:
                    self.booking_details["children_ages"] = children_ages
                
                return {"adults": adults, "children": children}
            except ValueError:
                print("❌ Please enter valid numbers.")
    
    def collect_preferences(self) -> Dict[str, Any]:
        """Collect user preferences for the hotel."""
        preferences = {}
        
        print("\n🌟 Hotel Preferences:")
        
        # Price range
        while True:
            try:
                min_price = float(input("💰 Minimum price per night (USD): "))
                max_price = float(input("💰 Maximum price per night (USD): "))
                
                if min_price < 0 or max_price < 0:
                    print("❌ Prices cannot be negative. Please try again.")
                    continue
                
                if min_price > max_price:
                    print("❌ Minimum price cannot be greater than maximum price. Please try again.")
                    continue
                
                preferences["price_range"] = {"min": min_price, "max": max_price}
                break
            except ValueError:
                print("❌ Please enter valid numbers.")
        
        # Star rating
        while True:
            try:
                min_stars = int(input("⭐ Minimum star rating (1-5): "))
                
                if min_stars < 1 or min_stars > 5:
                    print("❌ Star rating must be between 1 and 5. Please try again.")
                    continue
                
                preferences["min_stars"] = min_stars
                break
            except ValueError:
                print("❌ Please enter a valid number.")
        
        # Amenities
        print("\n🛎️ Select desired amenities (enter 'y' for yes, 'n' for no):")
        amenities = []
        
        if input("🏊 Swimming pool? (y/n): ").lower() == 'y':
            amenities.append("pool")
        
        if input("🍳 Free breakfast? (y/n): ").lower() == 'y':
            amenities.append("breakfast")
        
        if input("🅿️ Free parking? (y/n): ").lower() == 'y':
            amenities.append("parking")
        
        if input("🌐 Free WiFi? (y/n): ").lower() == 'y':
            amenities.append("wifi")
        
        if input("🏋️ Fitness center? (y/n): ").lower() == 'y':
            amenities.append("fitness")
        
        preferences["amenities"] = amenities
        self.booking_details["preferences"] = preferences
        
        return preferences
    
    def collect_all_details(self) -> Dict[str, Any]:
        """Collect all booking details from the user."""
        self.display_welcome_message()
        self.collect_destination()
        self.collect_dates()
        self.collect_guests_info()
        self.collect_preferences()
        
        print("\n✅ All booking details collected successfully!")
        return self.booking_details

# Agent2: Booking.com API Integration
class BookingAPIAgent:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get("BOOKING_API_KEY")
        if not self.api_key:
            raise ValueError("Booking.com API key is required. Set it in the environment variable BOOKING_API_KEY or pass it to the constructor.")
    
    def search_hotels(self, booking_details: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Search for hotels based on the booking details.
        
        In a real implementation, this would make API calls to Booking.com.
        For this example, we'll simulate the API response.
        """
        print(f"\n🔍 Searching for hotels in {booking_details['destination']}...")
        print(f"📅 Check-in: {booking_details['check_in']}, Check-out: {booking_details['check_out']}")
        print(f"👨‍👩‍👧‍👦 Guests: {booking_details['adults']} adults, {booking_details['children']} children")
        
        # Simulate API call delay
        import time
        time.sleep(2)
        
        # Simulate API response
        hotels = [
            {
                "id": "hotel1",
                "name": "Grand Hotel",
                "stars": 5,
                "price_per_night": 250.0,
                "total_price": 250.0 * (datetime.datetime.strptime(booking_details['check_out'], "%Y-%m-%d").date() - 
                                       datetime.datetime.strptime(booking_details['check_in'], "%Y-%m-%d").date()).days,
                "amenities": ["pool", "breakfast", "parking", "wifi", "fitness"],
                "rating": 9.2,
                "reviews": 1250,
                "address": "123 Main St, Downtown",
                "image_url": "https://example.com/grand_hotel.jpg"
            },
            {
                "id": "hotel2",
                "name": "Budget Inn",
                "stars": 3,
                "price_per_night": 120.0,
                "total_price": 120.0 * (datetime.datetime.strptime(booking_details['check_out'], "%Y-%m-%d").date() - 
                                       datetime.datetime.strptime(booking_details['check_in'], "%Y-%m-%d").date()).days,
                "amenities": ["wifi", "parking"],
                "rating": 7.8,
                "reviews": 850,
                "address": "456 Side St, Uptown",
                "image_url": "https://example.com/budget_inn.jpg"
            },
            {
                "id": "hotel3",
                "name": "Luxury Resort & Spa",
                "stars": 5,
                "price_per_night": 350.0,
                "total_price": 350.0 * (datetime.datetime.strptime(booking_details['check_out'], "%Y-%m-%d").date() - 
                                       datetime.datetime.strptime(booking_details['check_in'], "%Y-%m-%d").date()).days,
                "amenities": ["pool", "breakfast", "parking", "wifi", "fitness", "spa"],
                "rating": 9.7,
                "reviews": 2100,
                "address": "789 Beach Rd, Seaside",
                "image_url": "https://example.com/luxury_resort.jpg"
            }
        ]
        
        # Filter hotels based on preferences
        filtered_hotels = []
        preferences = booking_details.get("preferences", {})
        
        for hotel in hotels:
            # Filter by price range
            if preferences.get("price_range"):
                if hotel["price_per_night"] < preferences["price_range"]["min"] or \
                   hotel["price_per_night"] > preferences["price_range"]["max"]:
                    continue
            
            # Filter by star rating
            if preferences.get("min_stars") and hotel["stars"] < preferences["min_stars"]:
                continue
            
            # Filter by amenities
            if preferences.get("amenities"):
                if not all(amenity in hotel["amenities"] for amenity in preferences["amenities"]):
                    continue
            
            filtered_hotels.append(hotel)
        
        print(f"\n✅ Found {len(filtered_hotels)} hotels matching your criteria.")
        return filtered_hotels
    
    def book_hotel(self, hotel_id: str, booking_details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Book a hotel based on the selected hotel ID and booking details.
        
        In a real implementation, this would make API calls to Booking.com.
        For this example, we'll simulate the API response.
        """
        print(f"\n🏨 Booking hotel with ID: {hotel_id}...")
        
        # Simulate API call delay
        import time
        time.sleep(2)
        
        # Simulate booking confirmation
        booking_confirmation = {
            "booking_id": f"BK{int(time.time())}",
            "hotel_id": hotel_id,
            "check_in": booking_details["check_in"],
            "check_out": booking_details["check_out"],
            "guests": {
                "adults": booking_details["adults"],
                "children": booking_details["children"]
            },
            "status": "confirmed",
            "payment_status": "pending",
            "total_price": 0,  # This would be calculated based on the actual hotel
            "booking_date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        print(f"\n✅ Booking confirmed! Booking ID: {booking_confirmation['booking_id']}")
        return booking_confirmation

# Agent3: Integration Agent
class IntegrationAgent:
    def __init__(self, api_key: str = None):
        self.ui_agent = UserInterfaceAgent()
        self.booking_agent = BookingAPIAgent(api_key)
    
    def run(self):
        """Run the complete hotel booking process."""
        try:
            # Step 1: Collect user details
            booking_details = self.ui_agent.collect_all_details()
            
            # Step 2: Search for hotels
            hotels = self.booking_agent.search_hotels(booking_details)
            
            if not hotels:
                print("\n❌ No hotels found matching your criteria. Please try again with different preferences.")
                return
            
            # Step 3: Display hotel options
            print("\n🏨 Available Hotels:")
            for i, hotel in enumerate(hotels):
                print(f"\n{i+1}. {hotel['name']} ({'⭐' * hotel['stars']})")
                print(f"   💰 ${hotel['price_per_night']:.2f} per night (Total: ${hotel['total_price']:.2f})")
                print(f"   ⭐ Rating: {hotel['rating']}/10 ({hotel['reviews']} reviews)")
                print(f"   📍 {hotel['address']}")
                print(f"   🛎️ Amenities: {', '.join(hotel['amenities'])}")
            
            # Step 4: Let user select a hotel
            while True:
                try:
                    selection = int(input("\n🔢 Enter the number of the hotel you want to book (0 to cancel): "))
                    
                    if selection == 0:
                        print("\n❌ Booking cancelled.")
                        return
                    
                    if selection < 1 or selection > len(hotels):
                        print(f"❌ Please enter a number between 1 and {len(hotels)}.")
                        continue
                    
                    selected_hotel = hotels[selection-1]
                    break
                except ValueError:
                    print("❌ Please enter a valid number.")
            
            # Step 5: Confirm booking
            print(f"\n🏨 You selected: {selected_hotel['name']}")
            print(f"💰 Total price: ${selected_hotel['total_price']:.2f}")
            
            confirm = input("\n✅ Confirm booking? (y/n): ").lower()
            if confirm != 'y':
                print("\n❌ Booking cancelled.")
                return
            
            # Step 6: Book the hotel
            booking_confirmation = self.booking_agent.book_hotel(selected_hotel['id'], booking_details)
            
            # Step 7: Display booking confirmation
            print("\n" + "="*50)
            print("🎉 Booking Confirmation 🎉")
            print("="*50)
            print(f"Booking ID: {booking_confirmation['booking_id']}")
            print(f"Hotel: {selected_hotel['name']}")
            print(f"Check-in: {booking_confirmation['check_in']}")
            print(f"Check-out: {booking_confirmation['check_out']}")
            print(f"Guests: {booking_confirmation['guests']['adults']} adults, {booking_confirmation['guests']['children']} children")
            print(f"Total Price: ${selected_hotel['total_price']:.2f}")
            print(f"Booking Date: {booking_confirmation['booking_date']}")
            print(f"Status: {booking_confirmation['status']}")
            print("="*50)
            print("\nThank you for using our Automated Hotel Booking System! 🙏")
            
        except Exception as e:
            print(f"\n❌ An error occurred: {str(e)}")
            print("Please try again later.")

# Example usage
if __name__ == "__main__":
    # Set your Booking.com API key in the environment variable or pass it directly
    # os.environ["BOOKING_API_KEY"] = "your_api_key_here"
    
    
    # For demonstration purposes, we'll use a dummy API key
    booking_system = IntegrationAgent(api_key="dummy_api_key")
    booking_system.run()
