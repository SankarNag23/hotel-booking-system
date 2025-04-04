from flask import Flask, render_template, jsonify, request
from datetime import datetime, timedelta
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-123')

# Print startup message
print("Starting Hotel Booking System...")
print("Environment:", os.environ.get('FLASK_ENV', 'development'))
print("Server starting on port:", os.environ.get('PORT', 5000))

# In-memory database
HOTELS = [
    {
        "id": 1,
        "name": "Grand Hotel",
        "price": 200,
        "rating": 4,
        "description": "Luxury hotel in the city center with pool and spa.",
        "image": "https://images.unsplash.com/photo-1566073771259-6a8506099945?auto=format&w=800",
        "rooms_available": 5
    },
    {
        "id": 2,
        "name": "Seaside Resort",
        "price": 180,
        "rating": 5,
        "description": "Beautiful beachfront resort with ocean views.",
        "image": "https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?auto=format&w=800",
        "rooms_available": 3
    },
    {
        "id": 3,
        "name": "Budget Inn",
        "price": 120,
        "rating": 3,
        "description": "Comfortable and affordable accommodation.",
        "image": "https://images.unsplash.com/photo-1566665797739-1674de7a421a?auto=format&w=800",
        "rooms_available": 8
    }
]

# In-memory bookings storage
BOOKINGS = []

@app.route('/')
def index():
    try:
        return render_template('index.html')
    except Exception as e:
        print(f"Error rendering index: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/hotels')
def get_hotels():
    try:
        # Get filter parameters
        min_price = float(request.args.get('min_price', 0))
        max_price = float(request.args.get('max_price', 1000))
        min_rating = int(request.args.get('min_rating', 1))
        
        # Filter hotels based on criteria
        filtered_hotels = [
            hotel for hotel in HOTELS
            if min_price <= hotel['price'] <= max_price
            and hotel['rating'] >= min_rating
            and hotel['rooms_available'] > 0
        ]
        
        return jsonify({"success": True, "hotels": filtered_hotels})
    except Exception as e:
        print(f"Error getting hotels: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/hotels/<int:hotel_id>')
def get_hotel_details(hotel_id):
    try:
        hotel = next((h for h in HOTELS if h['id'] == hotel_id), None)
        if hotel:
            return jsonify({"success": True, "hotel": hotel})
        return jsonify({"success": False, "error": "Hotel not found"}), 404
    except Exception as e:
        print(f"Error getting hotel details: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/book', methods=['POST'])
def book_hotel():
    try:
        data = request.get_json()
        hotel_id = data.get('hotel_id')
        guest_name = data.get('guest_name')
        guest_email = data.get('guest_email')
        check_in = data.get('check_in')
        check_out = data.get('check_out')
        
        # Validate required fields
        if not all([hotel_id, guest_name, guest_email, check_in, check_out]):
            return jsonify({
                "success": False,
                "error": "Missing required booking information"
            }), 400
            
        # Find hotel and check availability
        hotel = next((h for h in HOTELS if h['id'] == hotel_id), None)
        if not hotel:
            return jsonify({
                "success": False,
                "error": "Hotel not found"
            }), 404
            
        if hotel['rooms_available'] <= 0:
            return jsonify({
                "success": False,
                "error": "No rooms available"
            }), 400
            
        # Create booking
        booking_id = f"BK{datetime.now().strftime('%Y%m%d%H%M%S')}"
        booking = {
            "booking_id": booking_id,
            "hotel_id": hotel_id,
            "guest_name": guest_name,
            "guest_email": guest_email,
            "check_in": check_in,
            "check_out": check_out,
            "total_price": hotel['price'],
            "status": "confirmed",
            "created_at": datetime.now().isoformat()
        }
        
        # Update availability
        hotel['rooms_available'] -= 1
        BOOKINGS.append(booking)
        
        return jsonify({
            "success": True,
            "booking": booking,
            "message": "Booking confirmed!"
        })
        
    except Exception as e:
        print(f"Error booking hotel: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/bookings/<booking_id>')
def get_booking(booking_id):
    try:
        booking = next((b for b in BOOKINGS if b['booking_id'] == booking_id), None)
        if booking:
            return jsonify({"success": True, "booking": booking})
        return jsonify({"success": False, "error": "Booking not found"}), 404
    except Exception as e:
        print(f"Error getting booking: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/health')
def health_check():
    """Health check endpoint for Render.com"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    print(f"Starting server on port {port}")
    print(f"Debug mode: {debug}")
    app.run(host='0.0.0.0', port=port, debug=debug) 