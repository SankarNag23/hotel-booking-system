# Automated Hotel Booking System V2.1

import os
import json
import datetime
import time
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import logging
import random
import string
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# Initialize FastAPI app
app = FastAPI(title="Hotel Booking System API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logger = logging.getLogger(__name__)

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
        print("🏨 Welcome to the Advanced Automated Hotel Booking System V2.1! 🏨")
        print("="*60 + "\n")
        print("🌟 Features:")
        print("  • Smart hotel recommendations")
        print("  • Real-time availability checking")
        print("  • Price comparison across multiple hotels")
        print("  • Special offers and discounts")
        print("  • Detailed hotel information and reviews")
        print("  • Enhanced search filters")
        print("  • Improved user interface")
        print("="*60 + "\n")
    
    def collect_destination(self) -> str:
        """Collect destination information from the user with validation."""
        while True:
            try:
                destination = input("📍 Enter your destination (city, country): ").strip()
                if len(destination) < 2:
                    print("❌ Destination name is too short. Please try again.")
                    continue
                if not destination.replace(" ", "").isalpha():
                    print("❌ Destination name should only contain letters and spaces. Please try again.")
                    continue
                self.booking_details["destination"] = destination
                logger.info(f"Destination selected: {destination}")
                return destination
            except Exception as e:
                logger.error(f"Error collecting destination: {str(e)}")
                print("❌ An error occurred. Please try again.")
    
    def collect_dates(self) -> tuple:
        """Collect check-in and check-out dates from the user with validation."""
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
                logger.info(f"Dates selected: Check-in {check_in_str}, Check-out {check_out_str}")
                return check_in_str, check_out_str
            except ValueError:
                print("❌ Invalid date format. Please use YYYY-MM-DD format.")
            except Exception as e:
                logger.error(f"Error collecting dates: {str(e)}")
                print("❌ An error occurred. Please try again.")
    
    def collect_guests_info(self) -> Dict[str, int]:
        """Collect information about the number of adults and children with validation."""
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
                
                logger.info(f"Guest information collected: {adults} adults, {children} children")
                return {"adults": adults, "children": children}
            except ValueError:
                print("❌ Please enter valid numbers.")
            except Exception as e:
                logger.error(f"Error collecting guest information: {str(e)}")
                print("❌ An error occurred. Please try again.")
    
    def collect_preferences(self) -> Dict[str, Any]:
        """Collect user preferences for the hotel with validation."""
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
            except Exception as e:
                logger.error(f"Error collecting price preferences: {str(e)}")
                print("❌ An error occurred. Please try again.")
        
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
            except Exception as e:
                logger.error(f"Error collecting star rating preference: {str(e)}")
                print("❌ An error occurred. Please try again.")
        
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
            except Exception as e:
                logger.error(f"Error collecting room type preference: {str(e)}")
                print("❌ An error occurred. Please try again.")
        
        # Amenities
        print("\n🛎️ Select desired amenities (enter 'y' for yes, 'n' for no):")
        amenities = []
        
        for amenity_id, amenity in self.amenities.items():
            while True:
                try:
                    choice = input(f"{amenity.icon} {amenity.name}? (y/n): ").lower()
                    if choice in ['y', 'n']:
                        if choice == 'y':
                            amenities.append(amenity_id)
                        break
                    print("❌ Please enter 'y' for yes or 'n' for no.")
                except Exception as e:
                    logger.error(f"Error collecting amenity preference: {str(e)}")
                    print("❌ An error occurred. Please try again.")
        
        preferences["amenities"] = amenities
        self.booking_details["preferences"] = preferences
        
        logger.info("Hotel preferences collected successfully")
        return preferences
    
    def collect_all_details(self) -> Dict[str, Any]:
        """Collect all booking details from the user with improved error handling."""
        try:
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
            
            logger.info("All booking details collected successfully")
            return self.booking_details
        except Exception as e:
            logger.error(f"Error collecting booking details: {str(e)}")
            print("❌ An error occurred while collecting booking details. Please try again.")
            return None

class BookingAPIAgent:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get("BOOKING_API_KEY")
        if not self.api_key:
            raise ValueError("Booking.com API key is required. Set it in the environment variable BOOKING_API_KEY or pass it to the constructor.")
        logger.info("BookingAPIAgent initialized successfully")
    
    def search_hotels(self, booking_details: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Search for hotels based on the booking details.
        
        In a real implementation, this would make API calls to Booking.com.
        For this example, we'll simulate the API response.
        """
        try:
            logger.info(f"Searching hotels in {booking_details['destination']}")
            logger.info(f"Check-in: {booking_details['check_in']}, Check-out: {booking_details['check_out']}")
            logger.info(f"Guests: {booking_details['adults']} adults, {booking_details['children']} children")
            
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
                    "rating": 4.8,
                    "reviews": 1200,
                    "amenities": ["pool", "breakfast", "wifi", "fitness", "spa"],
                    "room_types": ["Standard", "Deluxe", "Suite"],
                    "description": "Luxury hotel in the heart of the city",
                    "location": "City Center",
                    "highlights": ["City View", "Luxury Spa", "Fine Dining"],
                    "nearby_attractions": ["Shopping Mall", "Museum", "Park"],
                    "image_url": "https://images.unsplash.com/photo-1542314831-068cd1dbfeeb?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80"
                },
                {
                    "id": "hotel2",
                    "name": "Beach Resort",
                    "stars": 4,
                    "price_per_night": 180.0,
                    "total_price": 180.0 * (datetime.datetime.strptime(booking_details['check_out'], "%Y-%m-%d").date() - 
                                          datetime.datetime.strptime(booking_details['check_in'], "%Y-%m-%d").date()).days,
                    "rating": 4.5,
                    "reviews": 800,
                    "amenities": ["pool", "breakfast", "wifi", "fitness", "restaurant"],
                    "room_types": ["Standard", "Deluxe"],
                    "description": "Beachfront resort with stunning ocean views",
                    "location": "Beachfront",
                    "highlights": ["Ocean View", "Beach Access", "Water Sports"],
                    "nearby_attractions": ["Beach", "Water Park", "Shopping Center"],
                    "image_url": "https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80"
                }
            ]
            
            # Filter hotels based on preferences
            filtered_hotels = []
            for hotel in hotels:
                if hotel["stars"] < booking_details["preferences"]["min_stars"]:
                    continue
                if hotel["price_per_night"] < booking_details["preferences"]["price_range"]["min"] or \
                   hotel["price_per_night"] > booking_details["preferences"]["price_range"]["max"]:
                    continue
                if not all(amenity in hotel["amenities"] for amenity in booking_details["preferences"]["amenities"]):
                    continue
                if booking_details["preferences"]["room_type"] not in hotel["room_types"]:
                    continue
                filtered_hotels.append(hotel)
            
            logger.info(f"Found {len(filtered_hotels)} hotels matching criteria")
            return filtered_hotels
        except Exception as e:
            logger.error(f"Error searching hotels: {str(e)}")
            return []

class IntegrationAgent:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get("BOOKING_API_KEY")
        if not self.api_key:
            raise ValueError("Booking.com API key is required. Set it in the environment variable BOOKING_API_KEY or pass it to the constructor.")
        logger.info("IntegrationAgent initialized successfully")
    
    def process_booking(self, hotel_id: str, booking_details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a hotel booking with improved error handling and validation.
        
        In a real implementation, this would:
        1. Check hotel availability
        2. Process payment
        3. Create booking record in database
        4. Send confirmation email
        """
        try:
            # Validate booking details
            if not hotel_id:
                raise ValueError("Hotel ID is required")
            
            if not booking_details.get("check_in") or not booking_details.get("check_out"):
                raise ValueError("Check-in and check-out dates are required")
            
            # Generate booking reference
            booking_ref = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            
            # Create booking record
            booking = {
                "reference": booking_ref,
                "hotel_id": hotel_id,
                "check_in": booking_details["check_in"],
                "check_out": booking_details["check_out"],
                "guests": {
                    "adults": booking_details["adults"],
                    "children": booking_details.get("children", 0)
                },
                "preferences": booking_details.get("preferences", {}),
                "status": "confirmed",
                "created_at": datetime.datetime.now().isoformat()
            }
            
            logger.info(f"Booking processed successfully with reference: {booking_ref}")
            return booking
        except ValueError as e:
            logger.error(f"Validation error in booking process: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error processing booking: {str(e)}")
            raise

if __name__ == "__main__":
    # Initialize and run the booking system
    booking_system = IntegrationAgent()
    booking_system.run() 