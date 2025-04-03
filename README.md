# Hotel Booking System

A modern, responsive hotel booking system built with Node.js, Express, TypeScript, and MongoDB. The frontend is designed with Tailwind CSS for a beautiful and mobile-friendly user interface.

## Features

- Responsive design that works on all devices
- Real-time hotel search and filtering
- User authentication and authorization
- Secure booking system
- Admin dashboard for hotel management
- RESTful API architecture

## Prerequisites

- Node.js (v14 or higher)
- MongoDB (v4.4 or higher)
- npm or yarn package manager

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/hotel-booking-system.git
cd hotel-booking-system
```

2. Install dependencies:
```bash
npm install
```

3. Create a `.env` file in the root directory and add the following variables:
```env
PORT=3000
MONGODB_URI=mongodb://localhost:27017/hotel-booking
NODE_ENV=development
```

4. Start MongoDB:
```bash
# On Windows
net start MongoDB

# On macOS/Linux
sudo service mongod start
```

## Development

1. Start the development server:
```bash
npm run dev
```

2. Build the project:
```bash
npm run build
```

3. Run tests:
```bash
npm test
```

## Project Structure

```
hotel-booking-system/
├── src/
│   ├── server.ts
│   ├── models/
│   ├── routes/
│   └── controllers/
├── public/
│   ├── index.html
│   ├── css/
│   └── js/
├── tests/
├── package.json
├── tsconfig.json
└── .env
```

## API Endpoints

### Hotels
- `GET /api/hotels` - Get all hotels
- `GET /api/hotels/:id` - Get hotel by ID
- `POST /api/hotels/search` - Search hotels by location and dates

### Bookings
- `POST /api/bookings` - Create a new booking
- `GET /api/bookings/:id` - Get booking by ID
- `PUT /api/bookings/:id` - Update booking
- `DELETE /api/bookings/:id` - Cancel booking

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Tailwind CSS](https://tailwindcss.com/) for the beautiful UI components
- [MongoDB](https://www.mongodb.com/) for the database
- [Express](https://expressjs.com/) for the web framework 