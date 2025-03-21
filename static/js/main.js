document.addEventListener('DOMContentLoaded', function() {
    // Initialize date pickers
    const checkInPicker = flatpickr("#checkIn", {
        dateFormat: "Y-m-d",
        minDate: "today",
        onChange: function(selectedDates, dateStr) {
            checkOutPicker.set("minDate", dateStr);
            if (checkOutPicker.selectedDates[0] && checkOutPicker.selectedDates[0] < selectedDates[0]) {
                checkOutPicker.setDate(selectedDates[0]);
            }
        }
    });

    const checkOutPicker = flatpickr("#checkOut", {
        dateFormat: "Y-m-d",
        minDate: "today",
        onChange: function(selectedDates, dateStr) {
            if (selectedDates[0] < checkInPicker.selectedDates[0]) {
                checkOutPicker.setDate(checkInPicker.selectedDates[0]);
            }
        }
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
const bookingForm = document.getElementById("bookingForm");
if (bookingForm) {
    bookingForm.addEventListener("submit", async function(e) {
        e.preventDefault();
        
        const destination = document.getElementById("destination").value;
        const checkIn = document.getElementById("checkIn").value;
        const checkOut = document.getElementById("checkOut").value;
        const guests = document.getElementById("guests").value;

        if (!destination || !checkIn || !checkOut) {
            showAlert("Please fill in all required fields", "error");
            return;
        }

        showLoading();
        try {
            const response = await fetch("/api/search", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    destination,
                    checkIn,
                    checkOut,
                    guests: parseInt(guests)
                })
            });

            if (!response.ok) {
                throw new Error("Search failed");
            }

            const data = await response.json();
            displaySearchResults(data);
            document.getElementById("searchResults").scrollIntoView({ behavior: "smooth" });
        } catch (error) {
            console.error("Search error:", error);
            showAlert("Failed to search hotels. Please try again.", "error");
        } finally {
            hideLoading();
        }
    });
}

// Display search results
function displaySearchResults(hotels) {
    const hotelList = document.getElementById("hotelList");
    if (!hotelList) return;

    hotelList.innerHTML = "";
    document.getElementById("searchResults").style.display = "block";

    hotels.forEach(hotel => {
        const hotelCard = createHotelCard(hotel);
        hotelList.appendChild(hotelCard);
    });
}

// Create hotel card
function createHotelCard(hotel) {
    const div = document.createElement("div");
    div.className = "col-md-6 col-lg-4 mb-4";
    div.innerHTML = `
        <div class="hotel-card">
            <img src="${hotel.image}" alt="${hotel.name}" class="lazy">
            <div class="hotel-info">
                <h3>${hotel.name}</h3>
                <div class="rating mb-2">
                    ${createStarRating(hotel.rating)}
                </div>
                <p class="location">
                    <i class="fas fa-map-marker-alt"></i> ${hotel.location}
                </p>
                <div class="amenities mb-2">
                    ${createAmenitiesList(hotel.amenities)}
                </div>
                <div class="price-info">
                    <span class="price">$${hotel.price}</span>
                    <span class="per-night">per night</span>
                    </div>
                <button class="btn btn-primary w-100" onclick="bookHotel('${hotel.id}')">
                        Book Now
                    </button>
                </div>
            </div>
        `;
    return div;
}

// Create star rating
function createStarRating(rating) {
    const fullStars = Math.floor(rating);
    const hasHalfStar = rating % 1 !== 0;
    let stars = "";
    
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

// Create amenities list
function createAmenitiesList(amenities) {
    return amenities.map(amenity => `
        <span class="amenity">
            <i class="fas fa-${getAmenityIcon(amenity)}"></i>
            ${amenity}
        </span>
    `).join("");
}

// Get amenity icon
function getAmenityIcon(amenity) {
    const icons = {
        "WiFi": "wifi",
        "Pool": "swimming-pool",
        "Gym": "dumbbell",
        "Restaurant": "utensils",
        "Spa": "spa",
        "Bar": "glass-martini-alt",
        "Parking": "parking",
        "Room Service": "concierge-bell"
    };
    return icons[amenity] || "check";
}

// Show destination details
function showDestinationDetails(destination) {
    const modal = new bootstrap.Modal(document.getElementById("destinationModal"));
    const content = document.getElementById("destinationContent");
    
    // Mock destination data (replace with API call)
    const destinations = {
        "new-york": {
            name: "New York City",
            description: "The city that never sleeps offers world-class hotels in iconic locations.",
            highlights: [
                "Times Square",
                "Central Park",
                "Broadway",
                "Statue of Liberty"
            ],
            image: "https://images.unsplash.com/photo-1538970272646-f61fabb3a8a2?ixlib=rb-1.2.1&auto=format&fit=crop&w=1950&q=80"
        },
        "london": {
            name: "London",
            description: "Experience luxury and history in the heart of the British capital.",
            highlights: [
                "Big Ben",
                "Buckingham Palace",
                "Tower Bridge",
                "Westminster Abbey"
            ],
            image: "https://images.unsplash.com/photo-1513635269975-59663e0ac1ad?ixlib=rb-1.2.1&auto=format&fit=crop&w=1950&q=80"
        },
        "paris": {
            name: "Paris",
            description: "Discover romance and elegance in the City of Light.",
            highlights: [
                "Eiffel Tower",
                "Louvre Museum",
                "Notre-Dame",
                "Arc de Triomphe"
            ],
            image: "https://images.unsplash.com/photo-1502602898657-3e91760cbb34?ixlib=rb-1.2.1&auto=format&fit=crop&w=1950&q=80"
        },
        "tokyo": {
            name: "Tokyo",
            description: "Immerse yourself in the perfect blend of tradition and modernity.",
            highlights: [
                "Shibuya Crossing",
                "Senso-ji Temple",
                "Tokyo Skytree",
                "Meiji Shrine"
            ],
            image: "https://images.unsplash.com/photo-1503899036084-c55cdd92da26?ixlib=rb-1.2.1&auto=format&fit=crop&w=1950&q=80"
        }
    };

    const dest = destinations[destination];
    if (!dest) return;

    content.innerHTML = `
        <div class="destination-details">
            <img src="${dest.image}" alt="${dest.name}" class="img-fluid rounded mb-4">
            <h3>${dest.name}</h3>
            <p>${dest.description}</p>
            <h4>Highlights</h4>
            <ul class="list-unstyled">
                ${dest.highlights.map(highlight => `
                    <li><i class="fas fa-check text-success me-2"></i>${highlight}</li>
                `).join("")}
            </ul>
        </div>
    `;

    modal.show();
}

// Focus destination input
function focusDestination() {
    const destinationInput = document.getElementById("destination");
    if (destinationInput) {
        destinationInput.focus();
    }
}

// Show loading state
function showLoading() {
    const loading = document.createElement("div");
    loading.className = "loading-overlay";
    loading.innerHTML = `
        <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
        </div>
        <p class="mt-2">Searching for hotels...</p>
    `;
    document.body.appendChild(loading);
}

// Hide loading state
function hideLoading() {
    const loading = document.querySelector(".loading-overlay");
    if (loading) {
        loading.remove();
    }
}

// Show alert message
function showAlert(message, type = "info") {
    const alert = document.createElement("div");
    alert.className = `alert alert-${type} alert-dismissible fade show`;
    alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.body.insertBefore(alert, document.body.firstChild);
    setTimeout(() => alert.remove(), 5000);
}

// Book hotel
function bookHotel(hotelId) {
    // Implement booking logic
    showAlert("Booking functionality coming soon!", "info");
}

// Handle filter changes
document.querySelectorAll(".filters-card input, .filters-card select").forEach(filter => {
    filter.addEventListener("change", function() {
        // Implement filter logic
        showAlert("Filters applied!", "info");
    });
}); 