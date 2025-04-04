// Simplified location data with only essential information
const locationData = {
    'Maldives': {
        image: 'https://images.unsplash.com/photo-1566073771259-6a8506099945?auto=format&fit=crop&w=800&q=80',
        features: ['Overwater Bungalows', 'Private Beaches', 'Coral Reefs']
    },
    'Bali': {
        image: 'https://images.unsplash.com/photo-1582719508461-905c673771fd?auto=format&fit=crop&w=800&q=80',
        features: ['Rice Terraces', 'Temple Tours', 'Surf Spots']
    },
    'Swiss Alps': {
        image: 'https://images.unsplash.com/photo-1542314831-068cd1dbfeeb?auto=format&fit=crop&w=800&q=80',
        features: ['Ski Resorts', 'Mountain Views', 'Hiking Trails']
    }
};

// Simple background image update
function updateBackgroundImage(location) {
    const data = locationData[location];
    if (!data) return;

    const backgroundContainer = document.querySelector('.background-container') || createBackgroundContainer();
    backgroundContainer.style.backgroundImage = `url(${data.image})`;
}

// Create background container if it doesn't exist
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
    `;
    document.body.insertBefore(container, document.body.firstChild);
    return container;
}

// Simple location autocomplete
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

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    initLocationAutocomplete();
    updateBackgroundImage('Maldives');
}); 