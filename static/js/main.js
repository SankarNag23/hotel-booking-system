document.addEventListener('DOMContentLoaded', function() {
    // Initialize date pickers
    const dateConfig = {
        minDate: "today",
        altInput: true,
        altFormat: "F j, Y",
        dateFormat: "Y-m-d",
    };
    
    flatpickr("#checkIn", {
        ...dateConfig,
        onChange: function(selectedDates) {
            checkOut._flatpickr.set("minDate", selectedDates[0]);
        }
    });
    
    const checkOut = flatpickr("#checkOut", dateConfig);

    // Handle form submission
    document.getElementById('searchForm').addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const formData = new FormData(this);
        const params = new URLSearchParams();
        
        params.append('min_price', document.getElementById('minPrice').value);
        params.append('max_price', document.getElementById('maxPrice').value);
        params.append('min_stars', 1);
        
        // Add selected amenities
        const amenities = ['pool', 'wifi', 'breakfast', 'fitness'];
        amenities.forEach(amenity => {
            if (document.getElementById(amenity).checked) {
                params.append('amenities', amenity);
            }
        });

        try {
            const response = await fetch(`/api/hotels?${params.toString()}`);
            const data = await response.json();
            displayHotels(data.hotels);
        } catch (error) {
            console.error('Error:', error);
            alert('An error occurred while searching for hotels.');
        }
    });
});

function displayHotels(hotels) {
    const resultsContainer = document.getElementById('searchResults');
    resultsContainer.innerHTML = '';

    if (hotels.length === 0) {
        resultsContainer.innerHTML = `
            <div class="col-12 text-center">
                <h3>No hotels found matching your criteria</h3>
                <p>Please try adjusting your search parameters.</p>
            </div>
        `;
        return;
    }

    hotels.forEach(hotel => {
        const card = document.createElement('div');
        card.className = 'col-md-6 col-lg-4 mb-4';
        card.innerHTML = `
            <div class="card hotel-card h-100">
                <img src="${hotel.image}" class="card-img-top" alt="${hotel.name}">
                <div class="card-body">
                    <h5 class="card-title">${hotel.name}</h5>
                    <div class="hotel-rating">
                        ${'⭐'.repeat(hotel.stars)} 
                        <span class="text-muted">(${hotel.rating}/10 from ${hotel.reviews} reviews)</span>
                    </div>
                    <p class="card-text">${hotel.description}</p>
                    <div class="hotel-amenities">
                        ${hotel.amenities.map(amenity => `
                            <span class="amenity-badge">${getAmenityEmoji(amenity)} ${amenity}</span>
                        `).join('')}
                    </div>
                    <p class="hotel-price">$${hotel.price_per_night} <small>per night</small></p>
                    <button class="btn btn-primary w-100" onclick="showBookingModal(${JSON.stringify(hotel)})">
                        Book Now
                    </button>
                </div>
            </div>
        `;
        resultsContainer.appendChild(card);
    });
}

function getAmenityEmoji(amenity) {
    const emojiMap = {
        'pool': '🏊',
        'wifi': '📶',
        'breakfast': '🍳',
        'fitness': '🏋️',
        'parking': '🅿️',
        'spa': '💆',
        'beach-access': '🏖️'
    };
    return emojiMap[amenity] || '🏨';
}

function showBookingModal(hotel) {
    const checkIn = document.getElementById('checkIn').value;
    const checkOut = document.getElementById('checkOut').value;
    const adults = document.getElementById('adults').value;
    const children = document.getElementById('children').value;

    const nights = calculateNights(checkIn, checkOut);
    const totalPrice = hotel.price_per_night * nights;

    const modalBody = document.getElementById('bookingDetails');
    modalBody.innerHTML = `
        <div class="booking-summary">
            <h4>${hotel.name}</h4>
            <p class="text-muted">${hotel.address}</p>
            <hr>
            <div class="row">
                <div class="col-md-6">
                    <p><strong>Check-in:</strong> ${formatDate(checkIn)}</p>
                    <p><strong>Check-out:</strong> ${formatDate(checkOut)}</p>
                    <p><strong>Nights:</strong> ${nights}</p>
                </div>
                <div class="col-md-6">
                    <p><strong>Adults:</strong> ${adults}</p>
                    <p><strong>Children:</strong> ${children}</p>
                    <p><strong>Room Type:</strong> Standard</p>
                </div>
            </div>
            <hr>
            <div class="d-flex justify-content-between align-items-center">
                <h5>Total Price:</h5>
                <h5 class="text-primary">$${totalPrice}</h5>
            </div>
        </div>
    `;

    document.getElementById('confirmBooking').onclick = () => confirmBooking(hotel, {
        check_in: checkIn,
        check_out: checkOut,
        guests: { adults: parseInt(adults), children: parseInt(children) },
        nights: nights,
        total_price: totalPrice
    });

    const modal = new bootstrap.Modal(document.getElementById('bookingModal'));
    modal.show();
}

function calculateNights(checkIn, checkOut) {
    const start = new Date(checkIn);
    const end = new Date(checkOut);
    return Math.ceil((end - start) / (1000 * 60 * 60 * 24));
}

function formatDate(dateStr) {
    return new Date(dateStr).toLocaleDateString('en-US', {
        weekday: 'short',
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

async function confirmBooking(hotel, bookingDetails) {
    try {
        const response = await fetch('/api/book', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                hotel_id: hotel.id,
                ...bookingDetails
            })
        });

        const data = await response.json();
        
        if (data.booking) {
            const modal = bootstrap.Modal.getInstance(document.getElementById('bookingModal'));
            modal.hide();
            alert('Booking confirmed! Your booking ID is: ' + data.booking.booking_id);
        } else {
            alert('Error: ' + data.error);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred while confirming your booking.');
    }
} 