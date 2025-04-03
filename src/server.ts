import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import path from 'path';

// Load environment variables
dotenv.config();

const app = express();
const port = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Serve static files from the public directory
const publicPath = path.join(__dirname, '../public');
app.use(express.static(publicPath));
app.use('/js', express.static(path.join(publicPath, 'js')));
app.use('/css', express.static(path.join(publicPath, 'css')));
app.use('/images', express.static(path.join(publicPath, 'images')));

// Log static file requests in development
if (process.env.NODE_ENV === 'development') {
    app.use((req, res, next) => {
        console.log(`[${new Date().toISOString()}] ${req.method} ${req.url}`);
        next();
    });
}

// In-memory hotel data
const hotels = [
    {
        id: '1',
        name: 'Luxury Resort',
        location: 'Maldives',
        description: 'Experience luxury in paradise',
        price: 299,
        rating: 4.8,
        images: ['https://images.unsplash.com/photo-1566073771259-6a8506099945'],
        amenities: ['Pool', 'Spa', 'Beach Access', 'Fine Dining']
    },
    {
        id: '2',
        name: 'Beach Villa',
        location: 'Bali',
        description: 'Beachfront villa with stunning views',
        price: 199,
        rating: 4.5,
        images: ['https://images.unsplash.com/photo-1582719508461-905c673771fd'],
        amenities: ['Private Beach', 'Pool', 'Kitchen', 'WiFi']
    },
    {
        id: '3',
        name: 'Mountain Lodge',
        location: 'Swiss Alps',
        description: 'Cozy mountain retreat with breathtaking views',
        price: 249,
        rating: 4.7,
        images: ['https://images.unsplash.com/photo-1542314831-068cd1dbfeeb'],
        amenities: ['Fireplace', 'Ski Access', 'Hot Tub', 'Restaurant']
    }
];

// API Routes
app.get('/api/hotels', (req, res) => {
    res.json(hotels);
});

app.get('/api/hotels/:id', (req, res) => {
    const hotel = hotels.find(h => h.id === req.params.id);
    if (!hotel) {
        return res.status(404).json({ error: 'Hotel not found' });
    }
    res.json(hotel);
});

app.post('/api/hotels/search', (req, res) => {
    const { location, checkIn, checkOut } = req.body;
    const filteredHotels = hotels.filter(hotel => 
        hotel.location.toLowerCase().includes(location.toLowerCase())
    );
    res.json(filteredHotels);
});

// Serve index.html for all other routes (client-side routing)
app.get('*', (req, res) => {
    res.sendFile(path.join(publicPath, 'index.html'));
});

// Error handling middleware
app.use((err: Error, req: express.Request, res: express.Response, next: express.NextFunction) => {
    console.error(err.stack);
    res.status(500).json({ error: 'Something went wrong!' });
});

// Start server
app.listen(port, () => {
    console.log(`Server is running on port ${port}`);
    console.log(`Serving static files from: ${publicPath}`);
}); 