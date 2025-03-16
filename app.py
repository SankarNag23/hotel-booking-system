from flask import Flask, render_template, jsonify, request
from datetime import datetime
import os
import asyncio
from services.hotel_aggregator import HotelAggregator

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-123')

# Initialize the hotel aggregator
hotel_aggregator = HotelAggregator()

# Print startup message
print("Starting Hotel Booking System...")
print("Environment:", os.environ.get('FLASK_ENV', 'development'))
print("Server starting on port:", os.environ.get('PORT', 5000))

# In-memory database (we'll enhance this later)
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
async def get_hotels():
    try:
        # Get filter parameters
        min_price = float(request.args.get('min_price', 0))
        max_price = float(request.args.get('max_price', 1000))
        min_rating = int(request.args.get('min_rating', 1))
        location = request.args.get('location', 'New York')  # Default location
        check_in = datetime.strptime(request.args.get('check_in', datetime.now().strftime('%Y-%m-%d')), '%Y-%m-%d')
        check_out = datetime.strptime(request.args.get('check_out', (datetime.now() + datetime.timedelta(days=1)).strftime('%Y-%m-%d')), '%Y-%m-%d')
        guests = int(request.args.get('guests', 2))

        # Prepare filters
        filters = {
            'min_price': min_price,
            'max_price': max_price,
            'min_rating': min_rating,
            'no_payment_only': request.args.get('no_payment_only', '').lower() == 'true',
            'free_cancellation_only': request.args.get('free_cancellation_only', '').lower() == 'true'
        }

        # Search hotels using the aggregator
        results = await hotel_aggregator.search_hotels(
            location=location,
            check_in=check_in,
            check_out=check_out,
            guests=guests,
            filters=filters
        )

        return jsonify({"success": True, "results": results})
    except Exception as e:
        print(f"Error getting hotels: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/hotels/<hotel_id>')
async def get_hotel_details(hotel_id):
    try:
        check_in = datetime.strptime(request.args.get('check_in', datetime.now().strftime('%Y-%m-%d')), '%Y-%m-%d')
        check_out = datetime.strptime(request.args.get('check_out', (datetime.now() + datetime.timedelta(days=1)).strftime('%Y-%m-%d')), '%Y-%m-%d')
        guests = int(request.args.get('guests', 2))

        details = await hotel_aggregator.get_hotel_details(
            hotel_id=hotel_id,
            check_in=check_in,
            check_out=check_out,
            guests=guests
        )

        return jsonify({"success": True, "hotel": details})
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
        "version": "2.0.0"
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    print(f"Starting server on port {port}")
    print(f"Debug mode: {debug}")
    app.run(host='0.0.0.0', port=port, debug=debug) 