from flask import Flask, render_template, jsonify, request
from datetime import datetime
import os

app = Flask(__name__)

# Hotel data
HOTELS = [
    {
        "id": 1,
        "name": "Grand Hotel",
        "price": 200,
        "rating": 4,
        "description": "Luxury hotel in the city center with pool and spa.",
        "image": "https://images.unsplash.com/photo-1566073771259-6a8506099945?auto=format&w=800"
    },
    {
        "id": 2,
        "name": "Seaside Resort",
        "price": 180,
        "rating": 5,
        "description": "Beautiful beachfront resort with ocean views.",
        "image": "https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?auto=format&w=800"
    },
    {
        "id": 3,
        "name": "Budget Inn",
        "price": 120,
        "rating": 3,
        "description": "Comfortable and affordable accommodation.",
        "image": "https://images.unsplash.com/photo-1566665797739-1674de7a421a?auto=format&w=800"
    }
]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/hotels')
def get_hotels():
    return jsonify({"success": True, "hotels": HOTELS})

@app.route('/api/book', methods=['POST'])
def book_hotel():
    try:
        data = request.get_json()
        booking_id = f"BK{datetime.now().strftime('%Y%m%d%H%M%S')}"
        return jsonify({
            "success": True,
            "booking_id": booking_id,
            "message": "Booking confirmed!"
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port) 