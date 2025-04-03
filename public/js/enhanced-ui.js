// Location data with images and videos
const locationData = {
    'Maldives': {
        image: 'https://images.unsplash.com/photo-1566073771259-6a8506099945',
        video: 'https://player.vimeo.com/external/454453561.sd.mp4?s=8a71ff0f6a4bfba32687866fdfb5891ae71bd462&profile_id=164&oauth2_token_id=57447761',
        features: ['Overwater Bungalows', 'Private Beaches', 'Coral Reefs'],
        mustVisit: ['Male Atoll', 'Maafushi Island', 'Hulhumale'],
        rooms: [
            { type: 'Water Villa', features: ['Ocean View', 'Private Pool', 'Butler Service'] },
            { type: 'Beach Suite', features: ['Beachfront', 'Garden', 'Spa Access'] }
        ]
    },
    'Bali': {
        image: 'https://images.unsplash.com/photo-1582719508461-905c673771fd',
        video: 'https://player.vimeo.com/external/368763160.sd.mp4?s=13543e173b4b2b3a96491b9f6e24e2a8b5a89049&profile_id=164&oauth2_token_id=57447761',
        features: ['Rice Terraces', 'Temple Tours', 'Surf Spots'],
        mustVisit: ['Ubud', 'Seminyak', 'Uluwatu Temple'],
        rooms: [
            { type: 'Pool Villa', features: ['Private Pool', 'Garden View', 'Outdoor Shower'] },
            { type: 'Ocean Suite', features: ['Ocean View', 'Balcony', 'Beach Access'] }
        ]
    },
    'Swiss Alps': {
        image: 'https://images.unsplash.com/photo-1542314831-068cd1dbfeeb',
        video: 'https://player.vimeo.com/external/370467553.sd.mp4?s=96de8b923370e0cc6d82c9cf45f5eb5d427f2694&profile_id=164&oauth2_token_id=57447761',
        features: ['Ski Resorts', 'Mountain Views', 'Hiking Trails'],
        mustVisit: ['Zermatt', 'Interlaken', 'Lucerne'],
        rooms: [
            { type: 'Chalet Suite', features: ['Mountain View', 'Fireplace', 'Private Terrace'] },
            { type: 'Alpine Room', features: ['Ski-in/Ski-out', 'Heated Floors', 'Spa Access'] }
        ]
    }
};

// Initialize location autocomplete
function initLocationAutocomplete() {
    const locationInput = document.getElementById('location-input');
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

    // Hide autocomplete on click outside
    document.addEventListener('click', (e) => {
        if (!locationInput.contains(e.target)) {
            autocompleteList.classList.add('hidden');
        }
    });
}

// Update background image based on location
function updateBackgroundImage(location) {
    const data = locationData[location];
    if (data) {
        document.body.style.backgroundImage = `url(${data.image})`;
        document.body.style.backgroundSize = 'cover';
        document.body.style.backgroundPosition = 'center';
        document.body.style.transition = 'background-image 0.5s ease-in-out';
    }
}

// Convert featured hotel cards to video cards
function initVideoCards() {
    const hotelCards = document.querySelectorAll('.group.relative');
    hotelCards.forEach(card => {
        const location = card.querySelector('h3').textContent.trim();
        const data = locationData[location];
        if (data) {
            // Replace image with video
            const imgContainer = card.querySelector('.aspect-w-1');
            const video = document.createElement('video');
            video.className = 'w-full h-full object-cover';
            video.loop = true;
            video.muted = true;
            video.autoplay = true;
            video.src = data.video;
            imgContainer.innerHTML = '';
            imgContainer.appendChild(video);

            // Add click handler for details popup
            card.addEventListener('click', () => showLocationDetails(location));
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
        <div class="bg-white rounded-lg p-8 max-w-2xl w-full mx-4 max-h-90vh overflow-auto">
            <div class="flex justify-between items-start">
                <h2 class="text-2xl font-bold mb-4">${location}</h2>
                <button class="text-gray-500 hover:text-gray-700" onclick="this.closest('.fixed').remove()">
                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                </button>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                    <h3 class="font-bold mb-2">Features</h3>
                    <ul class="list-disc pl-5 mb-4">
                        ${data.features.map(f => `<li>${f}</li>`).join('')}
                    </ul>
                    <h3 class="font-bold mb-2">Must Visit</h3>
                    <ul class="list-disc pl-5">
                        ${data.mustVisit.map(m => `<li>${m}</li>`).join('')}
                    </ul>
                </div>
                <div>
                    <h3 class="font-bold mb-2">Available Rooms</h3>
                    ${data.rooms.map(room => `
                        <div class="mb-4">
                            <h4 class="font-semibold">${room.type}</h4>
                            <ul class="list-disc pl-5">
                                ${room.features.map(f => `<li>${f}</li>`).join('')}
                            </ul>
                        </div>
                    `).join('')}
                </div>
            </div>
        </div>
    `;
    document.body.appendChild(popup);
}

// Initialize enhanced UI features
document.addEventListener('DOMContentLoaded', () => {
    initLocationAutocomplete();
    initVideoCards();
}); 