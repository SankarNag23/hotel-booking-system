"""
Main entry point for the Hotel Booking System
Version: 2.1.2
"""

from flask import Flask, request, render_template, jsonify
from flask_cors import CORS
import os
import logging
from datetime import datetime, timedelta
import random
import string
import httpx
from app.hotel_booking_system_v2 import UserInterfaceAgent, BookingAPIAgent, IntegrationAgent
from dotenv import load_dotenv
from app.hotel_providers import HotelDataProvider
from app.middleware import SecurityHeadersMiddleware
from app.validators import BookingRequest, sanitize_search_params, validate_api_key, validate_hotel_id, sanitize_log_data

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize agents
ui_agent = UserInterfaceAgent()
booking_agent = BookingAPIAgent()
integration_agent = IntegrationAgent()

# Mount static files and templates
app.static_folder = 'static'
app.template_folder = 'templates'

@app.route("/", methods=['GET'])
def read_root():
    """Render the main page with improved error handling"""
    try:
        return render_template("index.html")
    except Exception as e:
        logger.error(f"Error rendering index.html: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route("/health", methods=['GET'])
def health_check():
    """Health check endpoint with detailed status"""
    try:
        # Check if templates directory exists
        if not os.path.exists(app.template_folder):
            return jsonify({
                "status": "unhealthy",
                "reason": "templates directory not found",
                "version": "2.1.2"
            }), 500

        # Check if static directory exists
        if not os.path.exists(app.static_folder):
            return jsonify({
                "status": "unhealthy",
                "reason": "static directory not found",
                "version": "2.1.2"
            }), 500

        return jsonify({
            "status": "healthy",
            "version": "2.1.2",
            "timestamp": datetime.utcnow().isoformat(),
            "environment": os.getenv("FLASK_ENV", "production")
        })
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            "status": "unhealthy",
            "reason": str(e),
            "version": "2.1.2"
        }), 500

@app.route("/api/search", methods=['POST'])
def search_hotels():
    """Search for hotels with improved security and validation"""
    try:
        data = request.get_json()
        # Sanitize and validate search parameters
        sanitized_params = sanitize_search_params(data)
        
        # Get hotels from Google Places API
        hotels = booking_agent.search_hotels(sanitized_params)
        
        # Log sample hotel data (sanitized)
        if hotels:
            safe_hotel = sanitize_log_data(hotels[0])
            logger.info(f"Sample hotel: {safe_hotel['name']} in {safe_hotel['location']}")
        
        return jsonify({"hotels": hotels})
    except Exception as e:
        logger.error(f"Error searching hotels: {str(e)}")
        return jsonify({"error": "Failed to search hotels"}), 500

@app.route("/api/book", methods=['POST'])
def book_hotel():
    """Book a hotel with enhanced security and validation"""
    try:
        data = request.get_json()
        # Validate hotel ID
        if not validate_hotel_id(data["hotel_id"]):
            return jsonify({"error": "Invalid hotel ID"}), 400
        
        # Generate secure booking reference
        booking_ref = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        
        # Log sanitized booking data
        safe_data = sanitize_log_data(data)
        logger.info(f"Processing booking: {safe_data}")
        
        return jsonify({
            "status": "success",
            "booking": {
                "reference": booking_ref,
                "hotel_id": data["hotel_id"],
                "check_in": data["check_in"],
                "check_out": data["check_out"],
                "guests": data["guests"],
                "room_type": data["room_type"],
                "name": data["name"],
                "email": data["email"],
                "phone": data["phone"],
                "destination": data["destination"],
                "adults": data["adults"],
                "children": data["children"],
                "preferences": data["preferences"]
            }
        })
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Error processing booking: {str(e)}")
        return jsonify({"error": "Failed to process booking"}), 500

@app.route("/api/amenities", methods=['GET'])
def get_amenities():
    """Get list of available amenities"""
    return jsonify({
        "status": "success",
        "amenities": ui_agent.amenities
    })

@app.route("/api/room-types", methods=['GET'])
def get_room_types():
    """Get list of available room types"""
    from app.hotel_booking_system_v2 import RoomType
    return jsonify({
        "status": "success",
        "room_types": [{"id": rt.name, "name": rt.value} for rt in RoomType]
    })

@app.route('/destinations')
def destinations():
    return render_template('destinations.html')

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8000"))
    ) 