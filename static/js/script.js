// Search form submission
document.getElementById('search-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    // Show loading overlay
    document.getElementById('loading-overlay').style.display = 'flex';
    
    try {
        const formData = {
            destination: document.getElementById('destination').value,
            check_in: document.getElementById('check-in').value,
            check_out: document.getElementById('check-out').value,
            guests: parseInt(document.getElementById('guests').value),
            price_range: parseFloat(document.getElementById('price-range').value) || null,
            amenities: Array.from(document.querySelectorAll('input[name="amenities"]:checked')).map(cb => cb.value)
        };

        const response = await fetch('/api/search', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        displaySearchResults(data.hotels);
        
        // Scroll to results
        document.getElementById('search-results').scrollIntoView({ behavior: 'smooth' });
    } catch (error) {
        console.error('Error:', error);
        showAlert('Error searching hotels. Please try again.', 'error');
    } finally {
        // Hide loading overlay
        document.getElementById('loading-overlay').style.display = 'none';
    }
});

// Function to display search results
function displaySearchResults(hotels) {
    const resultsContainer = document.getElementById('search-results');
    resultsContainer.innerHTML = '';

    if (!hotels || hotels.length === 0) {
        resultsContainer.innerHTML = '<p class="no-results">No hotels found matching your criteria.</p>';
        return;
    }

    const resultsGrid = document.createElement('div');
    resultsGrid.className = 'results-grid';

    hotels.forEach(hotel => {
        const card = createHotelCard(hotel);
        resultsGrid.appendChild(card);
    });

    resultsContainer.appendChild(resultsGrid);
}

// Function to create hotel card
function createHotelCard(hotel) {
    const card = document.createElement('div');
    card.className = 'hotel-card';
    card.innerHTML = `
        <div class="hotel-image">
            <img src="${hotel.image_url}" alt="${hotel.name}" loading="lazy">
        </div>
        <div class="hotel-info">
            <h3>${hotel.name}</h3>
            <p class="location"><i class="fas fa-map-marker-alt"></i> ${hotel.location}</p>
            <div class="rating">
                <span class="stars">${'★'.repeat(hotel.stars)}</span>
                <span class="review-count">(${hotel.reviews} reviews)</span>
            </div>
            <div class="amenities">
                ${hotel.amenities.slice(0, 4).map(amenity => 
                    `<span class="amenity"><i class="fas fa-${getAmenityIcon(amenity)}"></i> ${amenity}</span>`
                ).join('')}
            </div>
            <div class="price">
                <span class="amount">$${hotel.price_per_night}</span>
                <span class="per-night">per night</span>
            </div>
            <button class="book-now" onclick="showBookingForm('${hotel.id}', '${hotel.name}')">Book Now</button>
        </div>
    `;
    return card;
}

// Function to handle popular destination clicks
function showDestinationDetails(destination) {
    const destinationData = {
        'new york': {
            video: '/static/videos/new-york.mp4',
            images: [
                '/static/images/ny-central-park.jpg',
                '/static/images/ny-times-square.jpg',
                '/static/images/ny-statue-liberty.jpg'
            ],
            trivia: [
                'Home to over 8.4 million people',
                'More than 800 languages are spoken in New York',
                'The New York subway system has 472 stations'
            ],
            attractions: [
                { name: 'Central Park', description: '843 acres of urban parkland' },
                { name: 'Times Square', description: 'Major commercial intersection and tourist destination' },
                { name: 'Statue of Liberty', description: 'Symbol of freedom and democracy' }
            ]
        },
        'london': {
            video: '/static/videos/london.mp4',
            images: [
                '/static/images/london-bridge.jpg',
                '/static/images/london-eye.jpg',
                '/static/images/buckingham-palace.jpg'
            ],
            trivia: [
                'Over 300 languages are spoken in London',
                'The London Underground is the oldest underground railway network in the world',
                'Big Ben is actually the name of the bell, not the tower'
            ],
            attractions: [
                { name: 'Tower Bridge', description: 'Iconic symbol of London' },
                { name: 'London Eye', description: 'Giant Ferris wheel on the South Bank' },
                { name: 'Buckingham Palace', description: 'Official residence of the British monarch' }
            ]
        },
        // Add more destinations...
    };

    const data = destinationData[destination.toLowerCase()];
    if (!data) return;

    const modal = document.createElement('div');
    modal.className = 'destination-modal';
    modal.innerHTML = `
        <div class="modal-content">
            <span class="close">&times;</span>
            <video autoplay loop muted playsinline>
                <source src="${data.video}" type="video/mp4">
                Your browser does not support the video tag.
            </video>
            <div class="destination-details">
                <h2>${destination}</h2>
                <div class="trivia-section">
                    <h3>Did You Know?</h3>
                    <ul>
                        ${data.trivia.map(fact => `<li>${fact}</li>`).join('')}
                    </ul>
                </div>
                <div class="attractions-grid">
                    ${data.attractions.map((attraction, index) => `
                        <div class="attraction-card">
                            <img src="${data.images[index]}" alt="${attraction.name}">
                            <h4>${attraction.name}</h4>
                            <p>${attraction.description}</p>
                        </div>
                    `).join('')}
                </div>
            </div>
        </div>
    `;

    document.body.appendChild(modal);

    const closeBtn = modal.querySelector('.close');
    closeBtn.onclick = () => modal.remove();

    window.onclick = (event) => {
        if (event.target === modal) {
            modal.remove();
        }
    };
}

// Function to update dynamic content on page load
function updateDynamicContent() {
    const vibeImages = [
        { url: '/static/images/vibe1.jpg', caption: 'Luxury Resorts' },
        { url: '/static/images/vibe2.jpg', caption: 'City Adventures' },
        { url: '/static/images/vibe3.jpg', caption: 'Beach Getaways' },
        { url: '/static/images/vibe4.jpg', caption: 'Mountain Retreats' }
    ];

    const vibeSection = document.createElement('section');
    vibeSection.className = 'vibe-section';
    vibeSection.innerHTML = `
        <h2>Travel Vibes</h2>
        <div class="vibe-grid">
            ${vibeImages.map(image => `
                <div class="vibe-card">
                    <img src="${image.url}" alt="${image.caption}">
                    <div class="vibe-caption">${image.caption}</div>
                </div>
            `).join('')}
        </div>
    `;

    // Insert after popular destinations section
    const popularSection = document.querySelector('.popular-destinations');
    popularSection.parentNode.insertBefore(vibeSection, popularSection.nextSibling);
}

// Call updateDynamicContent on page load
document.addEventListener('DOMContentLoaded', updateDynamicContent);

// Update guests input to be a number input with higher limit
const guestsInput = document.getElementById('guests');
guestsInput.type = 'number';
guestsInput.min = '1';
guestsInput.max = '10';
guestsInput.value = '1'; 