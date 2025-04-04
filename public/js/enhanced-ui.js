// Location data with enhanced information
const locationData = {
    'Maldives': {
        image: 'https://images.unsplash.com/photo-1566073771259-6a8506099945?auto=format&fit=crop&w=1920&q=80',
        features: ['Overwater Bungalows', 'Private Beaches', 'Coral Reefs'],
        mustVisit: ['Male Atoll', 'Maafushi Island', 'Hulhumale'],
        rooms: [
            { type: 'Water Villa', features: ['Ocean View', 'Private Pool', 'Butler Service'] },
            { type: 'Beach Suite', features: ['Beachfront', 'Garden', 'Spa Access'] }
        ]
    },
    'Bali': {
        image: 'https://images.unsplash.com/photo-1582719508461-905c673771fd?auto=format&fit=crop&w=1920&q=80',
        features: ['Rice Terraces', 'Temple Tours', 'Surf Spots'],
        mustVisit: ['Ubud', 'Seminyak', 'Uluwatu Temple'],
        rooms: [
            { type: 'Pool Villa', features: ['Private Pool', 'Garden View', 'Outdoor Shower'] },
            { type: 'Ocean Suite', features: ['Ocean View', 'Balcony', 'Beach Access'] }
        ]
    },
    'Swiss Alps': {
        image: 'https://images.unsplash.com/photo-1542314831-068cd1dbfeeb?auto=format&fit=crop&w=1920&q=80',
        features: ['Ski Resorts', 'Mountain Views', 'Hiking Trails'],
        mustVisit: ['Zermatt', 'Interlaken', 'Lucerne'],
        rooms: [
            { type: 'Chalet Suite', features: ['Mountain View', 'Fireplace', 'Private Terrace'] },
            { type: 'Alpine Room', features: ['Ski-in/Ski-out', 'Heated Floors', 'Spa Access'] }
        ]
    }
};

// Background image update with enhanced size
function updateBackgroundImage(location) {
    const data = locationData[location];
    if (!data) return;

    const backgroundContainer = document.querySelector('.background-container') || createBackgroundContainer();
    backgroundContainer.style.backgroundImage = `url(${data.image})`;
}

// Create background container with enhanced size
function createBackgroundContainer() {
    const container = document.createElement('div');
    container.className = 'background-container';
    container.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        z-index: -1;
        background-size: cover;
        background-position: center;
        transition: background-image 0.5s ease;
        min-height: 200vh;
    `;
    
    // Add overlay for better text visibility
    const overlay = document.createElement('div');
    overlay.style.cssText = `
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(to bottom, rgba(0,0,0,0.2), rgba(0,0,0,0.4));
    `;
    container.appendChild(overlay);
    
    document.body.insertBefore(container, document.body.firstChild);
    return container;
}

// Location autocomplete with enhanced UI
function initLocationAutocomplete() {
    const locationInput = document.getElementById('location-input');
    if (!locationInput) return;

    const autocompleteList = document.createElement('ul');
    autocompleteList.className = 'absolute z-10 w-full bg-white shadow-lg rounded-md mt-1 max-h-60 overflow-auto hidden';
    locationInput.parentNode.appendChild(autocompleteList);

    locationInput.addEventListener('input', (e) => {
        const value = e.target.value.toLowerCase();
        const matches = Object.keys(locationData).filter(location =>
            location.toLowerCase().includes(value)
        );

        autocompleteList.innerHTML = '';
        if (matches.length > 0 && value) {
            autocompleteList.classList.remove('hidden');
            matches.forEach(location => {
                const li = document.createElement('li');
                li.className = 'px-4 py-2 hover:bg-gray-100 cursor-pointer';
                li.textContent = location;
                li.addEventListener('click', () => {
                    locationInput.value = location;
                    autocompleteList.classList.add('hidden');
                    updateBackgroundImage(location);
                });
                autocompleteList.appendChild(li);
            });
        } else {
            autocompleteList.classList.add('hidden');
        }
    });

    document.addEventListener('click', (e) => {
        if (!locationInput.contains(e.target)) {
            autocompleteList.classList.add('hidden');
        }
    });
}

// Show location details popup
function showLocationDetails(location) {
    const data = locationData[location];
    if (!data) return;

    const popup = document.createElement('div');
    popup.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50';
    popup.innerHTML = `
        <div class="bg-white rounded-lg p-8 max-w-4xl w-full max-h-[90vh] overflow-y-auto transform transition-all duration-300">
            <div class="flex justify-between items-start mb-6">
                <h2 class="text-3xl font-bold text-gray-900">${location}</h2>
                <button class="text-gray-500 hover:text-gray-700">
                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                    </svg>
                </button>
            </div>
            
            <div class="mb-8">
                <h3 class="text-xl font-semibold mb-4">Features</h3>
                <div class="flex flex-wrap gap-2">
                    ${data.features.map(feature => `
                        <span class="px-3 py-1 bg-blue-100 text-blue-800 rounded-full">${feature}</span>
                    `).join('')}
                </div>
            </div>

            <div class="mb-8">
                <h3 class="text-xl font-semibold mb-4">Must Visit Places</h3>
                <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                    ${data.mustVisit.map(place => `
                        <div class="p-4 bg-gray-50 rounded-lg">
                            <h4 class="font-semibold mb-2">${place}</h4>
                            <p class="text-gray-600">Experience the beauty of ${place}</p>
                        </div>
                    `).join('')}
                </div>
            </div>

            <div class="mb-8">
                <h3 class="text-xl font-semibold mb-4">Available Rooms</h3>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    ${data.rooms.map(room => `
                        <div class="p-6 bg-gray-50 rounded-lg">
                            <h4 class="text-lg font-semibold mb-3">${room.type}</h4>
                            <ul class="space-y-2">
                                ${room.features.map(feature => `
                                    <li class="flex items-center text-gray-600">
                                        <svg class="w-5 h-5 mr-2 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                                        </svg>
                                        ${feature}
                                    </li>
                                `).join('')}
                            </ul>
                        </div>
                    `).join('')}
                </div>
            </div>

            <button class="w-full py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
                Book Now
            </button>
        </div>
    `;

    // Add close functionality
    const closeButton = popup.querySelector('button');
    closeButton.addEventListener('click', () => popup.remove());
    popup.addEventListener('click', (e) => {
        if (e.target === popup) popup.remove();
    });

    document.body.appendChild(popup);
}

// Initialize featured section
function initFeaturedSection() {
    const featuredCards = document.querySelectorAll('.hotel-card');
    featuredCards.forEach(card => {
        const location = card.getAttribute('data-location');
        if (!location) return;

        card.addEventListener('click', () => {
            showLocationDetails(location);
        });

        // Add hover effect
        card.addEventListener('mouseenter', () => {
            card.classList.add('transform', 'scale-105', 'shadow-xl');
        });

        card.addEventListener('mouseleave', () => {
            card.classList.remove('transform', 'scale-105', 'shadow-xl');
        });
    });
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    initLocationAutocomplete();
    initFeaturedSection();
    updateBackgroundImage('Maldives');
}); 