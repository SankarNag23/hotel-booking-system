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
        params.append('min_rating', document.getElementById('minRating').value);

        try {
            const response = await fetch(`/api/v1/hotels`);
            const data = await response.json();
            displayHotels(data);
        } catch (error) {
            console.error('Error:', error);
            alert('An error occurred while searching for hotels.');
        }
    });
});

function displayHotels(hotels) {
    const hotelList = document.getElementById('hotelList');
    hotelList.innerHTML = '';

    if (hotels.length === 0) {
        hotelList.innerHTML = `
            <div class="col-12 text-center">
                <h3>No hotels found matching your criteria</h3>
                <p>Please try adjusting your search parameters.</p>
            </div>
        `;
        return;
    }

    hotels.forEach(hotel => {
        const card = document.createElement('div');
        card.className = 'col-md-4 mb-4';
        card.innerHTML = `
            <div class="card h-100">
                <img src="${hotel.image}" class="card-img-top" alt="${hotel.name}">
                <div class="card-body">
                    <h5 class="card-title">${hotel.name}</h5>
                    <div class="mb-2">
                        ${'⭐'.repeat(hotel.rating)}
                    </div>
                    <p class="card-text">${hotel.description}</p>
                    <p class="card-text"><strong>Price:</strong> $${hotel.price} per night</p>
                    <p class="card-text"><small class="text-muted">Rooms available: ${hotel.rooms_available}</small></p>
                    <button class="btn btn-primary w-100" onclick="showBookingModal(${JSON.stringify(hotel)})">
                        Book Now
                    </button>
                </div>
            </div>
        `;
        hotelList.appendChild(card);
    });
}

function showBookingModal(hotel) {
    const modal = new bootstrap.Modal(document.getElementById('bookingModal'));
    
    // Set hotel ID in the form
    document.getElementById('hotelId').value = hotel.id;
    
    // Clear previous form values
    document.getElementById('guestName').value = '';
    document.getElementById('guestEmail').value = '';
    document.getElementById('checkIn').value = '';
    document.getElementById('checkOut').value = '';
    
    modal.show();
}

function confirmBooking() {
    const hotelId = document.getElementById('hotelId').value;
    const guestName = document.getElementById('guestName').value;
    const guestEmail = document.getElementById('guestEmail').value;
    const checkIn = document.getElementById('checkIn').value;
    const checkOut = document.getElementById('checkOut').value;

    if (!guestName || !guestEmail || !checkIn || !checkOut) {
        alert('Please fill in all required fields');
        return;
    }

    const bookingData = {
        hotelId: hotelId,
        guestName: guestName,
        guestEmail: guestEmail,
        checkIn: checkIn,
        checkOut: checkOut,
        guests: 2  // Default value
    };

    fetch('/api/v1/book', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(bookingData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Booking confirmed! Your booking ID is: ' + data.booking.booking_id);
            const modal = bootstrap.Modal.getInstance(document.getElementById('bookingModal'));
            modal.hide();
            // Refresh hotel list to update availability
            document.getElementById('searchForm').dispatchEvent(new Event('submit'));
        } else {
            alert('Error: ' + (data.error || 'Failed to create booking'));
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred while confirming your booking.');
    });
}

// Form validation
function validateForm() {
    const checkIn = document.getElementById('checkIn').value;
    const checkOut = document.getElementById('checkOut').value;
    const minPrice = document.getElementById('minPrice').value;
    const maxPrice = document.getElementById('maxPrice').value;
    
    if (!checkIn || !checkOut) {
        alert('Please select both check-in and check-out dates');
        return false;
    }
    
    if (new Date(checkOut) <= new Date(checkIn)) {
        alert('Check-out date must be after check-in date');
        return false;
    }
    
    if (parseFloat(minPrice) > parseFloat(maxPrice)) {
        alert('Minimum price cannot be greater than maximum price');
        return false;
    }
    
    return true;
}

// Date picker initialization
document.addEventListener('DOMContentLoaded', function() {
    const today = new Date();
    const tomorrow = new Date(today);
    tomorrow.setDate(tomorrow.getDate() + 1);
    
    // Set minimum dates for check-in and check-out
    document.getElementById('checkIn').min = today.toISOString().split('T')[0];
    document.getElementById('checkOut').min = tomorrow.toISOString().split('T')[0];
    
    // Update check-out minimum date when check-in changes
    document.getElementById('checkIn').addEventListener('change', function() {
        const checkInDate = new Date(this.value);
        const nextDay = new Date(checkInDate);
        nextDay.setDate(nextDay.getDate() + 1);
        document.getElementById('checkOut').min = nextDay.toISOString().split('T')[0];
    });
});

// Form data collection
HTMLFormElement.prototype.getFormData = function() {
    const formData = new FormData(this);
    const data = {};
    
    for (let [key, value] of formData.entries()) {
        data[key] = value;
    }
    
    return data;
};

// Loading state management
function setLoading(isLoading) {
    const searchButton = document.querySelector('button[type="submit"]');
    const hotelList = document.getElementById('hotelList');
    
    if (isLoading) {
        searchButton.disabled = true;
        searchButton.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Searching...';
        hotelList.innerHTML = '<div class="text-center"><div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div><p class="mt-2">Searching for hotels...</p></div>';
    } else {
        searchButton.disabled = false;
        searchButton.innerHTML = '<i class="fas fa-search me-2"></i>Search Hotels';
    }
}

// Error handling
function handleError(error) {
    console.error('Error:', error);
    const hotelList = document.getElementById('hotelList');
    hotelList.innerHTML = `
        <div class="alert alert-danger">
            <i class="fas fa-exclamation-circle me-2"></i>
            An error occurred while searching for hotels. Please try again.
        </div>
    `;
}

// Success message display
function showSuccess(message) {
    const alert = document.createElement('div');
    alert.className = 'alert alert-success alert-dismissible fade show';
    alert.innerHTML = `
        <i class="fas fa-check-circle me-2"></i>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.querySelector('.container').insertBefore(alert, document.querySelector('.row'));
    
    // Auto dismiss after 5 seconds
    setTimeout(() => {
        alert.remove();
    }, 5000);
}

// Price range validation
document.getElementById('minPrice').addEventListener('change', function() {
    const maxPrice = document.getElementById('maxPrice');
    if (parseFloat(this.value) > parseFloat(maxPrice.value)) {
        maxPrice.value = this.value;
    }
});

document.getElementById('maxPrice').addEventListener('change', function() {
    const minPrice = document.getElementById('minPrice');
    if (parseFloat(this.value) < parseFloat(minPrice.value)) {
        minPrice.value = this.value;
    }
});

// Guest count validation
document.getElementById('adults').addEventListener('change', function() {
    if (parseInt(this.value) < 1) {
        this.value = 1;
    }
});

document.getElementById('children').addEventListener('change', function() {
    if (parseInt(this.value) < 0) {
        this.value = 0;
    }
});

document.getElementById('bookingForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const amenities = [];
    document.querySelectorAll('input[type="checkbox"]:checked').forEach(checkbox => {
        amenities.push(checkbox.value);
    });
    
    const bookingRequest = {
        destination: document.getElementById('destination').value,
        check_in: document.getElementById('checkIn').value,
        check_out: document.getElementById('checkOut').value,
        adults: parseInt(document.getElementById('adults').value),
        children: parseInt(document.getElementById('children').value),
        preferences: {
            price_range: {
                min: parseFloat(document.getElementById('minPrice').value),
                max: parseFloat(document.getElementById('maxPrice').value)
            },
            min_stars: parseInt(document.getElementById('minStars').value),
            room_type: document.getElementById('roomType').value,
            amenities: amenities
        }
    };
    
    try {
        const response = await fetch('/api/search', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(bookingRequest)
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            displayHotels(data.hotels);
        } else {
            alert('Error searching for hotels. Please try again.');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error searching for hotels. Please try again.');
    }
});

function displayHotels(hotels) {
    const hotelList = document.getElementById('hotelList');
    hotelList.innerHTML = '';
    
    if (hotels.length === 0) {
        hotelList.innerHTML = '<div class="alert alert-info">No hotels found matching your criteria.</div>';
        return;
    }
    
    hotels.forEach(hotel => {
        const hotelCard = document.createElement('div');
        hotelCard.className = 'hotel-card p-4';
        
        const amenities = hotel.amenities.map(amenity => {
            const icons = {
                pool: 'fa-swimming-pool',
                breakfast: 'fa-utensils',
                parking: 'fa-parking',
                wifi: 'fa-wifi',
                fitness: 'fa-dumbbell',
                spa: 'fa-spa',
                restaurant: 'fa-utensils',
                bar: 'fa-glass-martini-alt',
                conference: 'fa-building',
                shuttle: 'fa-shuttle-van'
            };
            
            return `<span class="badge bg-success me-2">
                <i class="fas ${icons[amenity]} me-1"></i>${amenity}
            </span>`;
        }).join('');
        
        hotelCard.innerHTML = `
            <div class="row">
                <div class="col-md-4">
                    <img src="${hotel.image_url}" class="img-fluid rounded" alt="${hotel.name}">
                </div>
                <div class="col-md-8">
                    <h4>${hotel.name}</h4>
                    <p class="text-muted">
                        <i class="fas fa-map-marker-alt me-2"></i>${hotel.address}
                    </p>
                    <div class="mb-2">
                        ${Array(hotel.stars).fill('<i class="fas fa-star rating"></i>').join('')}
                        <span class="ms-2">(${hotel.rating}/10 - ${hotel.reviews} reviews)</span>
                    </div>
                    <p>${hotel.description}</p>
                    <div class="mb-2">
                        <strong>Available Room Types:</strong> ${hotel.room_types.join(', ')}
                    </div>
                    <div class="mb-2">
                        <strong>Amenities:</strong><br>
                        ${amenities}
                    </div>
                    <div class="d-flex justify-content-between align-items-center">
                        <div class="price-tag">
                            $${hotel.price_per_night} per night
                        </div>
                        <button class="btn btn-primary" onclick="bookHotel('${hotel.id}')">
                            <i class="fas fa-book me-2"></i>Book Now
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        hotelList.appendChild(hotelCard);
    });
}

async function bookHotel(hotelId) {
    try {
        const response = await fetch(`/api/book?hotel_id=${hotelId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(document.getElementById('bookingForm').getFormData())
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            alert(`Booking confirmed! Reference: ${data.confirmation.booking_reference}`);
        } else {
            alert('Error booking hotel. Please try again.');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error booking hotel. Please try again.');
    }
} 