# Hotel Booking System

A modern hotel booking system built with Flask and Bootstrap. Features include hotel search, filtering, real-time availability, and instant booking confirmation.

## Features

- Modern, responsive UI with Bootstrap 5
- Real-time hotel search and filtering
- Interactive date selection
- Instant booking confirmation
- Room availability tracking
- Booking management system

## Deployment on Render.com

1. Fork or clone this repository to your GitHub account
2. Go to [Render.com](https://render.com) and sign up/login
3. Click "New +" and select "Web Service"
4. Connect your GitHub repository
5. Fill in the following details:
   - Name: hotel-booking-system
   - Environment: Python 3
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
6. Click "Create Web Service"

The application will be automatically deployed and available at your Render URL.

## Environment Variables

Set the following environment variables in Render.com dashboard:
- `FLASK_ENV`: Set to 'production' for production deployment
- `SECRET_KEY`: Your secret key for session management

## Local Development

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python app.py
   ```

4. Visit http://localhost:5000 in your browser

## API Endpoints

- `GET /api/hotels` - List all available hotels with filtering options
- `POST /api/book` - Create a new booking
- `GET /api/bookings/<booking_id>` - Get booking details

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request 