import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import mongoose from 'mongoose';
import path from 'path';

// Load environment variables
dotenv.config();

const app = express();
const port = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(express.static(path.join(__dirname, '../public')));

// MongoDB connection
const MONGODB_URI = process.env.MONGODB_URI || 'mongodb://localhost:27017/hotel-booking';
mongoose.connect(MONGODB_URI)
    .then(() => console.log('Connected to MongoDB'))
    .catch((err) => console.error('MongoDB connection error:', err));

// Hotel Schema
const hotelSchema = new mongoose.Schema({
    name: String,
    location: String,
    description: String,
    price: Number,
    rating: Number,
    images: [String],
    amenities: [String],
    rooms: [{
        type: String,
        price: Number,
        capacity: Number
    }]
});

const Hotel = mongoose.model('Hotel', hotelSchema);

// Routes
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, '../public/index.html'));
});

// API Routes
app.get('/api/hotels', async (req, res) => {
    try {
        const hotels = await Hotel.find();
        res.json(hotels);
    } catch (error) {
        res.status(500).json({ error: 'Error fetching hotels' });
    }
});

app.get('/api/hotels/:id', async (req, res) => {
    try {
        const hotel = await Hotel.findById(req.params.id);
        if (!hotel) {
            return res.status(404).json({ error: 'Hotel not found' });
        }
        res.json(hotel);
    } catch (error) {
        res.status(500).json({ error: 'Error fetching hotel' });
    }
});

app.post('/api/hotels/search', async (req, res) => {
    try {
        const { location, checkIn, checkOut } = req.body;
        const hotels = await Hotel.find({
            location: { $regex: location, $options: 'i' }
        });
        res.json(hotels);
    } catch (error) {
        res.status(500).json({ error: 'Error searching hotels' });
    }
});

// Error handling middleware
app.use((err: Error, req: express.Request, res: express.Response, next: express.NextFunction) => {
    console.error(err.stack);
    res.status(500).json({ error: 'Something went wrong!' });
});

// Start server
app.listen(port, () => {
    console.log(`Server is running on port ${port}`);
}); 