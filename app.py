from flask import Flask, jsonify
import os

app = Flask(__name__)

@app.route('/health')
def health_check():
    return jsonify({
        "status": "healthy",
        "version": "2.1.2",
        "environment": os.getenv("FLASK_ENV", "production")
    })

@app.route('/')
def home():
    return jsonify({
        "message": "Hotel Booking System API",
        "status": "operational"
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 8000))) 