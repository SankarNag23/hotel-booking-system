from flask import Flask, render_template, jsonify, request
from datetime import datetime, timedelta
import os
from services.hotel_providers import HotelProviderFactory

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-123')

# Initialize hotel provider
hotel_provider = HotelProviderFactory()

# Print startup message
print("Starting Hotel Booking System...")
print("Environment:", os.environ.get('FLASK_ENV', 'development'))
print("Server starting on port:", os.environ.get('PORT', 5000))

@app.route('/')
def index():
    try:
        return render_template('index.html')
    except Exception as e:
        print(f"Error rendering index: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/v1/locations')
def search_locations():
    query = request.args.get('q', '')
    locations = hotel_provider.search_locations(query)
    return jsonify(locations)

@app.route('/api/v1/hotels')
def list_hotels():
    # Get search parameters
    location = request.args.get('location', 'New York City')  # Default to NYC
    check_in = request.args.get('check_in', datetime.now().strftime('%Y-%m-%d'))
    check_out = request.args.get('check_out', (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'))
    guests = int(request.args.get('guests', 2))
    min_price = request.args.get('min_price')
    max_price = request.args.get('max_price')
    min_rating = request.args.get('min_rating')

    hotels = hotel_provider.search_hotels(
        location=location,
        check_in=check_in,
        check_out=check_out,
        guests=guests,
        min_price=min_price,
        max_price=max_price,
        min_rating=min_rating
    )
    return jsonify(hotels)

@app.route('/api/v1/hotels/<hotel_id>')
def get_hotel(hotel_id):
    hotel = hotel_provider.get_hotel_details(hotel_id)
    if hotel is None:
        return jsonify({'error': 'Hotel not found'}), 404
    return jsonify(hotel)

@app.route('/api/v1/book', methods=['POST'])
def book_hotel():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    booking = hotel_provider.create_booking(data)
    if booking is None:
        return jsonify({'error': 'Failed to create booking'}), 500
    
    return jsonify({
        'success': True,
        'booking': booking,
        'message': 'Booking confirmed!'
    })

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