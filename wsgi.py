"""
WSGI entry point for the Hotel Booking System
"""

from app.app import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 