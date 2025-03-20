# Automated Hotel Booking System V2

import os
import json
import datetime
import time
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

class RoomType(Enum):
    STANDARD = "Standard"
    DELUXE = "Deluxe"
    SUITE = "Suite"
    PRESIDENTIAL = "Presidential"

@dataclass
class HotelAmenity:
    name: str
    description: str
    icon: str

class UserInterfaceAgent:
    def __init__(self):
        self.booking_details = {}
        self.amenities = {
            "pool": HotelAmenity("Swimming Pool", "Indoor and outdoor pools", "🏊"),
            "breakfast": HotelAmenity("Free Breakfast", "Complimentary breakfast buffet", "🍳"),
            "parking": HotelAmenity("Free Parking", "Secure parking facility", "🅿️"),
            "wifi": HotelAmenity("Free WiFi", "High-speed internet access", "🌐"),
            "fitness": HotelAmenity("Fitness Center", "24/7 gym access", "🏋️"),
            "spa": HotelAmenity("Spa", "Luxury spa services", "💆"),
            "restaurant": HotelAmenity("Restaurant", "On-site dining", "🍽️"),
            "bar": HotelAmenity("Bar", "Lounge and bar", "🍸"),
            "conference": HotelAmenity("Conference Room", "Business meeting facilities", "💼"),
            "shuttle": HotelAmenity("Airport Shuttle", "Complimentary airport transfer", "🚐")
        }
    
    def display_welcome_message(self):
        """Display a colorful welcome message to the user."""
        print("\n" + "="*60)
        print("🏨 Welcome to the Advanced Automated Hotel Booking System V2! 🏨")
        print("="*60 + "\n")
        print("🌟 Features:")
        print("  • Smart hotel recommendations")
        print("  • Real-time availability checking")
        print("  • Price comparison across multiple hotels")
        print("  • Special offers and discounts")
        print("  • Detailed hotel information and reviews")
        print("="*60 + "\n")
    
    def collect_destination(self) -> str:
        """Collect destination information from the user."""
        while True:
            destination = input("📍 Enter your destination (city, country): ").strip()
            if len(destination) < 2:
                print("❌ Destination name is too short. Please try again.")
                continue
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
                
                today = datetime.date.today()
                if check_in < today:
                    print("❌ Check-in date cannot be in the past. Please try again.")
                    continue
                
                if check_out <= check_in:
                    print("❌ Check-out date must be after check-in date. Please try again.")
                    continue
                
                # Check if booking is too far in the future (e.g., more than 1 year)
                max_future_date = today + datetime.timedelta(days=365)
                if check_out > max_future_date:
                    print("❌ Cannot book more than 1 year in advance. Please try again.")
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
                    while True:
                        try:
                            age = int(input(f"👶 Age of child {i+1}: "))
                            if age < 0 or age > 17:
                                print("❌ Child age must be between 0 and 17. Please try again.")
                                continue
                            children_ages.append(age)
                            break
                        except ValueError:
                            print("❌ Please enter a valid number.")
                
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
                
                if min_price < 50:
                    print("⚠️ Warning: Very low minimum price might limit available options.")
                
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
        
        # Room type preference
        print("\n🛏️ Select preferred room type:")
        for i, room_type in enumerate(RoomType, 1):
            print(f"{i}. {room_type.value}")
        
        while True:
            try:
                room_choice = int(input("Enter your choice (1-4): "))
                if 1 <= room_choice <= 4:
                    preferences["room_type"] = list(RoomType)[room_choice - 1].value
                    break
                print("❌ Invalid choice. Please try again.")
            except ValueError:
                print("❌ Please enter a valid number.")
        
        # Amenities
        print("\n🛎️ Select desired amenities (enter 'y' for yes, 'n' for no):")
        amenities = []
        
        for amenity_id, amenity in self.amenities.items():
            if input(f"{amenity.icon} {amenity.name}? (y/n): ").lower() == 'y':
                amenities.append(amenity_id)
        
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
        print("\n📋 Booking Summary:")
        print(f"Destination: {self.booking_details['destination']}")
        print(f"Check-in: {self.booking_details['check_in']}")
        print(f"Check-out: {self.booking_details['check_out']}")
        print(f"Guests: {self.booking_details['adults']} adults, {self.booking_details['children']} children")
        print(f"Room Type: {self.booking_details['preferences']['room_type']}")
        print(f"Price Range: ${self.booking_details['preferences']['price_range']['min']} - ${self.booking_details['preferences']['price_range']['max']} per night")
        print(f"Minimum Stars: {self.booking_details['preferences']['min_stars']}")
        print(f"Selected Amenities: {', '.join(self.booking_details['preferences']['amenities'])}")
        
        return self.booking_details

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
        time.sleep(2)
        
        # Simulate API response with more detailed hotel information
        hotels = [
            {
                "id": "hotel1",
                "name": "Grand Hotel",
                "stars": 5,
                "price_per_night": 250.0,
                "total_price": 250.0 * (datetime.datetime.strptime(booking_details['check_out'], "%Y-%m-%d").date() - 
                                       datetime.datetime.strptime(booking_details['check_in'], "%Y-%m-%d").date()).days,
                "amenities": ["pool", "breakfast", "parking", "wifi", "fitness", "spa", "restaurant", "bar", "conference"],
                "rating": 9.2,
                "reviews": 1250,
                "address": "123 Main St, Downtown",
                "image_url": "https://example.com/grand_hotel.jpg",
                "room_types": ["Standard", "Deluxe", "Suite"],
                "description": "Luxury hotel in the heart of downtown with world-class amenities.",
                "cancellation_policy": "Free cancellation up to 24 hours before check-in",
                "check_in_time": "15:00",
                "check_out_time": "12:00"
            },
            {
                "id": "hotel2",
                "name": "Budget Inn",
                "stars": 3,
                "price_per_night": 120.0,
                "total_price": 120.0 * (datetime.datetime.strptime(booking_details['check_out'], "%Y-%m-%d").date() - 
                                       datetime.datetime.strptime(booking_details['check_in'], "%Y-%m-%d").date()).days,
                "amenities": ["wifi", "parking", "breakfast"],
                "rating": 7.8,
                "reviews": 850,
                "address": "456 Side St, Uptown",
                "image_url": "https://example.com/budget_inn.jpg",
                "room_types": ["Standard"],
                "description": "Comfortable and affordable accommodation with essential amenities.",
                "cancellation_policy": "Free cancellation up to 48 hours before check-in",
                "check_in_time": "14:00",
                "check_out_time": "11:00"
            },
            {
                "id": "hotel3",
                "name": "Luxury Resort & Spa",
                "stars": 5,
                "price_per_night": 350.0,
                "total_price": 350.0 * (datetime.datetime.strptime(booking_details['check_out'], "%Y-%m-%d").date() - 
                                       datetime.datetime.strptime(booking_details['check_in'], "%Y-%m-%d").date()).days,
                "amenities": ["pool", "breakfast", "parking", "wifi", "fitness", "spa", "restaurant", "bar", "shuttle"],
                "rating": 9.7,
                "reviews": 2100,
                "address": "789 Beach Rd, Seaside",
                "image_url": "https://example.com/luxury_resort.jpg",
                "room_types": ["Deluxe", "Suite", "Presidential"],
                "description": "Exclusive beachfront resort with premium amenities and services.",
                "cancellation_policy": "Free cancellation up to 72 hours before check-in",
                "check_in_time": "16:00",
                "check_out_time": "12:00"
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
            
            # Filter by room type
            if preferences.get("room_type") and preferences["room_type"] not in hotel["room_types"]:
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
        time.sleep(2)
        
        # Generate a random booking reference
        booking_ref = f"BK{int(time.time())}{hotel_id[-4:]}"
        
        # Simulate successful booking
        booking_confirmation = {
            "booking_reference": booking_ref,
            "hotel_id": hotel_id,
            "status": "confirmed",
            "check_in": booking_details["check_in"],
            "check_out": booking_details["check_out"],
            "guests": {
                "adults": booking_details["adults"],
                "children": booking_details["children"]
            },
            "total_price": 0.0,  # This would be calculated based on the selected hotel
            "payment_status": "pending",
            "created_at": datetime.datetime.now().isoformat()
        }
        
        print(f"\n✅ Booking confirmed! Reference: {booking_ref}")
        return booking_confirmation

class IntegrationAgent:
    def __init__(self, api_key: str = None):
        self.ui_agent = UserInterfaceAgent()
        self.booking_agent = BookingAPIAgent(api_key)
    
    def display_hotel_options(self, hotels: List[Dict[str, Any]]):
        """Display hotel options in a formatted way."""
        print("\n🏨 Available Hotels:")
        print("="*80)
        
        for i, hotel in enumerate(hotels, 1):
            print(f"\n{i}. {hotel['name']} ({hotel['stars']}⭐)")
            print(f"   📍 {hotel['address']}")
            print(f"   💰 ${hotel['price_per_night']} per night")
            print(f"   ⭐ Rating: {hotel['rating']}/10 ({hotel['reviews']} reviews)")
            print(f"   🛏️ Room Types: {', '.join(hotel['room_types'])}")
            print(f"   🛎️ Amenities: {', '.join(hotel['amenities'])}")
            print(f"   📝 {hotel['description']}")
            print(f"   ⏰ Check-in: {hotel['check_in_time']}, Check-out: {hotel['check_out_time']}")
            print(f"   🔄 {hotel['cancellation_policy']}")
            print("-"*80)
    
    def select_hotel(self, hotels: List[Dict[str, Any]]) -> Optional[str]:
        """Let the user select a hotel from the available options."""
        while True:
            try:
                choice = int(input("\nEnter the number of your preferred hotel (or 0 to exit): "))
                if choice == 0:
                    return None
                if 1 <= choice <= len(hotels):
                    return hotels[choice - 1]["id"]
                print("❌ Invalid choice. Please try again.")
            except ValueError:
                print("❌ Please enter a valid number.")
    
    def run(self):
        """Main execution flow of the booking system."""
        try:
            # Collect booking details
            booking_details = self.ui_agent.collect_all_details()
            
            # Search for hotels
            hotels = self.booking_agent.search_hotels(booking_details)
            
            if not hotels:
                print("\n❌ No hotels found matching your criteria. Please try different preferences.")
                return
            
            # Display hotel options
            self.display_hotel_options(hotels)
            
            # Select hotel
            selected_hotel_id = self.select_hotel(hotels)
            if not selected_hotel_id:
                print("\n👋 Thank you for using our booking system!")
                return
            
            # Book the selected hotel
            booking_confirmation = self.booking_agent.book_hotel(selected_hotel_id, booking_details)
            
            print("\n🎉 Booking completed successfully!")
            print("="*60)
            print(f"Booking Reference: {booking_confirmation['booking_reference']}")
            print(f"Check-in: {booking_confirmation['check_in']}")
            print(f"Check-out: {booking_confirmation['check_out']}")
            print(f"Guests: {booking_confirmation['guests']['adults']} adults, {booking_confirmation['guests']['children']} children")
            print("="*60)
            
        except Exception as e:
            print(f"\n❌ An error occurred: {str(e)}")
            print("Please try again or contact support if the problem persists.")

if __name__ == "__main__":
    # Initialize and run the booking system
    booking_system = IntegrationAgent()
    booking_system.run() 