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