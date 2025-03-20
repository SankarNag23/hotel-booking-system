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
    document.getElementById('bookingForm').addEventListener('submit', async function(e) {
        e.preventDefault();
        
        if (!validateForm()) {
            return;
        }

        setLoading(true);

        try {
            // Get selected amenities
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
                        min: parseInt(document.getElementById('minPrice').value),
                        max: parseInt(document.getElementById('maxPrice').value)
                    },
                    min_stars: parseInt(document.getElementById('minStars').value),
                    room_type: document.getElementById('roomType').value,
                    amenities: amenities
                }
            };

            const response = await fetch('/api/search', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(bookingRequest)
            });

            if (!response.ok) {
                throw new Error('Search failed');
            }

            const data = await response.json();
            displayHotels(data.hotels);
        } catch (error) {
            handleError(error);
        } finally {
            setLoading(false);
        }
    });

    // Handle filter form changes
    document.getElementById('filterForm').addEventListener('change', function() {
        document.getElementById('bookingForm').dispatchEvent(new Event('submit'));
    });

    // Navbar scroll effect
    window.addEventListener('scroll', function() {
        const navbar = document.querySelector('.navbar');
        if (window.scrollY > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    });
});

function displayHotels(hotels) {
    const hotelList = document.getElementById('hotelList');
    hotelList.innerHTML = '';

    if (!hotels || hotels.length === 0) {
        hotelList.innerHTML = `
            <div class="alert alert-info">
                <i class="fas fa-info-circle me-2"></i>
                No hotels found matching your criteria. Please try adjusting your search parameters.
            </div>
        `;
        return;
    }

    hotels.forEach(hotel => {
        const card = document.createElement('div');
        card.className = 'hotel-card';
        card.innerHTML = `
            <div class="row">
                <div class="col-md-4">
                    <img src="${hotel.image_url}" class="img-fluid" alt="${hotel.name}">
                </div>
                <div class="col-md-8">
                    <div class="card-body">
                        <h4>${hotel.name}</h4>
                        <p class="text-muted">
                            <i class="fas fa-map-marker-alt me-2"></i>${hotel.address}
                        </p>
                        <div class="rating mb-2">
                            ${'⭐'.repeat(hotel.stars)} ${hotel.rating} (${hotel.reviews} reviews)
                        </div>
                        <p>${hotel.description}</p>
                        <div class="d-flex justify-content-between align-items-center mb-3">
                            <div class="price-tag">
                                <i class="fas fa-dollar-sign me-1"></i>${hotel.price_per_night} per night
                            </div>
                            <button class="btn btn-primary" onclick="bookHotel('${hotel.id}')">
                                <i class="fas fa-book me-2"></i>Book Now
                            </button>
                        </div>
                        <div class="amenities">
                            ${hotel.amenities.map(amenity => `
                                <span class="amenity-badge">
                                    <i class="fas fa-${getAmenityIcon(amenity)}"></i>${amenity}
                                </span>
                            `).join('')}
                        </div>
                    </div>
                </div>
            </div>
        `;
        hotelList.appendChild(card);
    });
}

function getAmenityIcon(amenity) {
    const icons = {
        pool: 'swimming-pool',
        breakfast: 'utensils',
        parking: 'parking',
        wifi: 'wifi',
        fitness: 'dumbbell',
        spa: 'spa',
        restaurant: 'utensils',
        bar: 'glass-martini-alt',
        conference: 'users'
    };
    return icons[amenity] || 'check';
}

async function bookHotel(hotelId) {
    try {
        const bookingRequest = {
            destination: document.getElementById('destination').value,
            check_in: document.getElementById('checkIn').value,
            check_out: document.getElementById('checkOut').value,
            adults: parseInt(document.getElementById('adults').value),
            children: parseInt(document.getElementById('children').value),
            preferences: {
                price_range: {
                    min: parseInt(document.getElementById('minPrice').value),
                    max: parseInt(document.getElementById('maxPrice').value)
                },
                min_stars: parseInt(document.getElementById('minStars').value),
                room_type: document.getElementById('roomType').value,
                amenities: Array.from(document.querySelectorAll('input[type="checkbox"]:checked')).map(cb => cb.value)
            }
        };

        const response = await fetch(`/api/book?hotel_id=${hotelId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(bookingRequest)
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Booking failed');
        }

        const data = await response.json();
        showSuccess(`Booking confirmed! Your booking reference is: ${data.confirmation.booking_reference}`);
    } catch (error) {
        handleError(error);
    }
}

// Form validation
function validateForm() {
    const checkIn = document.getElementById('checkIn').value;
    const checkOut = document.getElementById('checkOut').value;
    const minPrice = document.getElementById('minPrice').value;
    const maxPrice = document.getElementById('maxPrice').value;
    const destination = document.getElementById('destination').value;
    
    if (!destination) {
        alert('Please enter a destination');
        return false;
    }
    
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
            ${error.message || 'An error occurred while processing your request. Please try again.'}
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