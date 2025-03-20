document.addEventListener('DOMContentLoaded', function() {
    // Initialize flatpickr for date inputs
    flatpickr("#checkIn", {
        minDate: "today",
        dateFormat: "Y-m-d",
        onChange: function(selectedDates, dateStr, instance) {
            // Set minimum date for check-out to be check-in date
            checkOutPicker.set('minDate', dateStr);
        }
    });

    flatpickr("#checkOut", {
        minDate: "today",
        dateFormat: "Y-m-d"
    });

    // Initialize price range slider
    const priceRange = document.getElementById('priceRange');
    const priceValue = document.getElementById('priceValue');
    if (priceRange && priceValue) {
        priceRange.addEventListener('input', function() {
            priceValue.textContent = `$${this.value}`;
        });
    }

    // Initialize lazy loading
    const observer = lozad();
    observer.observe();

    // Add scroll animations
    const sections = document.querySelectorAll('section');
    const observerOptions = {
        threshold: 0.1
    };

    const sectionObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    }, observerOptions);

    sections.forEach(section => {
        sectionObserver.observe(section);
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

// Handle form submission
document.getElementById('bookingForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    // Show loading state
    const searchResults = document.getElementById('searchResults');
    const hotelList = document.getElementById('hotelList');
    searchResults.style.display = 'block';
    hotelList.innerHTML = '<div class="col-12 text-center"><div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div><p class="loading-text mt-3">Searching for the best hotels...</p></div>';

    // Get form data
    const formData = {
        destination: document.getElementById('destination').value,
        check_in: document.getElementById('checkIn').value,
        check_out: document.getElementById('checkOut').value,
        guests: document.getElementById('guests').value,
        price_range: document.getElementById('priceRange').value,
        amenities: getSelectedAmenities()
    };

    try {
        // Scroll to search results
        searchResults.scrollIntoView({ behavior: 'smooth' });

        // Make API request
        const response = await fetch('/api/search', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });

        if (!response.ok) {
            throw new Error('Search failed');
        }

        const data = await response.json();
        
        // Display hotels
        displayHotels(data.hotels);
    } catch (error) {
        console.error('Error:', error);
        hotelList.innerHTML = `
            <div class="col-12">
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-circle me-2"></i>
                    Error searching for hotels. Please try again.
                </div>
            </div>
        `;
    }
});

// Get selected amenities
function getSelectedAmenities() {
    const amenities = [];
    document.querySelectorAll('.amenities-grid input:checked').forEach(checkbox => {
        amenities.push(checkbox.id);
    });
    return amenities;
}

// Display hotels
function displayHotels(hotels) {
    const hotelList = document.getElementById('hotelList');
    
    if (!hotels || hotels.length === 0) {
        hotelList.innerHTML = `
            <div class="col-12">
                <div class="alert alert-info">
                    <i class="fas fa-info-circle me-2"></i>
                    No hotels found matching your criteria.
                </div>
            </div>
        `;
        return;
    }

    hotelList.innerHTML = hotels.map(hotel => `
        <div class="col-md-6 col-lg-4 mb-4">
            <div class="hotel-card">
                <img src="${hotel.image_url}" alt="${hotel.name}" class="lazy">
                <div class="card-body">
                    <h4>${hotel.name}</h4>
                    <p class="text-muted">
                        <i class="fas fa-map-marker-alt me-2"></i>${hotel.address}
                    </p>
                    <div class="rating mb-2">
                        ${generateStars(hotel.rating)}
                        <span class="ms-2">(${hotel.review_count} reviews)</span>
                    </div>
                    <div class="price-tag mb-3">
                        <i class="fas fa-tag me-2"></i>$${hotel.price_per_night}/night
                    </div>
                    <div class="amenities">
                        ${generateAmenities(hotel.amenities)}
                    </div>
                    <button class="btn btn-primary w-100 mt-3" onclick="bookHotel('${hotel.id}')">
                        <i class="fas fa-calendar-check me-2"></i>Book Now
                    </button>
                </div>
            </div>
        </div>
    `).join('');

    // Trigger lazy loading for new images
    const observer = lozad();
    observer.observe();
}

// Generate star rating HTML
function generateStars(rating) {
    const fullStars = Math.floor(rating);
    const hasHalfStar = rating % 1 !== 0;
    let stars = '';
    
    for (let i = 0; i < fullStars; i++) {
        stars += '<i class="fas fa-star text-warning"></i>';
    }
    
    if (hasHalfStar) {
        stars += '<i class="fas fa-star-half-alt text-warning"></i>';
    }
    
    const emptyStars = 5 - Math.ceil(rating);
    for (let i = 0; i < emptyStars; i++) {
        stars += '<i class="far fa-star text-warning"></i>';
    }
    
    return stars;
}

// Generate amenities HTML
function generateAmenities(amenities) {
    const amenityIcons = {
        wifi: 'fa-wifi',
        parking: 'fa-parking',
        pool: 'fa-swimming-pool',
        gym: 'fa-dumbbell',
        restaurant: 'fa-utensils',
        spa: 'fa-spa',
        bar: 'fa-glass-martini-alt',
        elevator: 'fa-elevator'
    };

    return amenities.map(amenity => `
        <span class="amenity-badge">
            <i class="fas ${amenityIcons[amenity] || 'fa-check'}"></i>
            ${amenity.charAt(0).toUpperCase() + amenity.slice(1)}
        </span>
    `).join('');
}

// Book hotel
async function bookHotel(hotelId) {
    try {
        const response = await fetch('/api/book', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                hotel_id: hotelId,
                check_in: document.getElementById('checkIn').value,
                check_out: document.getElementById('checkOut').value,
                guests: document.getElementById('guests').value
            })
        });

        if (!response.ok) {
            throw new Error('Booking failed');
        }

        const data = await response.json();
        
        // Show success message
        const hotelList = document.getElementById('hotelList');
        hotelList.innerHTML = `
            <div class="col-12">
                <div class="alert alert-success">
                    <i class="fas fa-check-circle me-2"></i>
                    Successfully booked ${data.hotel_name}! Your booking reference is: ${data.booking_reference}
                </div>
            </div>
        `;
    } catch (error) {
        console.error('Error:', error);
        const hotelList = document.getElementById('hotelList');
        hotelList.innerHTML = `
            <div class="col-12">
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-circle me-2"></i>
                    Error booking hotel. Please try again.
                </div>
            </div>
        `;
    }
}

// Handle filter changes
document.querySelectorAll('.filters-card input').forEach(input => {
    input.addEventListener('change', function() {
        // Re-trigger search with new filters
        document.getElementById('bookingForm').dispatchEvent(new Event('submit'));
    });
}); 