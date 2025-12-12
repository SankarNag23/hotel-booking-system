# Automated Hotel Booking System V2

A modern, user-friendly hotel booking system with advanced features and real-time availability checking.

## Features

- Smart hotel recommendations
- Real-time availability checking
- Price comparison across multiple hotels
- Special offers and discounts
- Detailed hotel information and reviews
- Room type selection
- Comprehensive amenities selection
- Guest management
- Flexible booking dates
- Cancellation policies

## Deployment on Render.com

1. Create a new Web Service on Render.com
2. Connect your GitHub repository
3. Configure the following settings:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python hotel_booking_system_v2.py`
   - Environment Variables:
     - `BOOKING_API_KEY`: Your Booking.com API key (if using real API)

## GitHub Codespaces (Recommended)

The easiest way to run this application is using GitHub Codespaces:

1. Click the green "Code" button on the GitHub repository
2. Select the "Codespaces" tab
3. Click "Create codespace on main" (or your preferred branch)
4. Wait for the environment to build (dependencies will be installed automatically)
5. Once ready, run the application:
   ```bash
   python main.py
   ```
6. The application will be available on port 8000
7. GitHub Codespaces will automatically forward the port - click the pop-up notification to open the app in your browser
8. Or go to the "Ports" tab in VS Code and click the globe icon next to port 8000

**Note:** The application runs on port 8000 (not 5173). Port 5173 is used by Vite dev servers, but this is a Flask application.

## Local Development

1. Clone the repository:
```bash
git clone https://github.com/SankarNag23/hotel-booking-system.git
cd hotel-booking-system
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python main.py
```

4. Open your browser and navigate to:
```
http://localhost:8000
```

## Output Validation

The system validates the following key points:

1. **Date Validation**:
   - Check-in date cannot be in the past
   - Check-out date must be after check-in date
   - Cannot book more than 1 year in advance

2. **Guest Information**:
   - At least 1 adult required
   - Maximum 10 guests total
   - Child ages must be between 0 and 17

3. **Price Range**:
   - Minimum price cannot be negative
   - Maximum price must be greater than minimum price
   - Warning for very low minimum prices (< $50)

4. **Hotel Selection**:
   - Room type must be available at selected hotel
   - Hotel must meet minimum star rating
   - Hotel must have all requested amenities
   - Price must be within specified range

## Testing

To test the output validation:

1. Run the application
2. Enter test data:
   - Destination: "New York, USA"
   - Check-in: Today's date
   - Check-out: Tomorrow's date
   - Guests: 2 adults, 1 child
   - Child age: 5
   - Price range: $100-$300
   - Minimum stars: 4
   - Room type: Standard
   - Select some amenities

3. Verify that:
   - All validations are working
   - Hotel options are filtered correctly
   - Booking confirmation is generated
   - All required information is displayed

## License

MIT License 