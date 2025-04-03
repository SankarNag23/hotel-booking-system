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
    },
    'London': {
        image: 'https://images.unsplash.com/photo-1513635269975-59663e0ac1ad',
        video: 'https://player.vimeo.com/external/371433846.sd.mp4?s=236da2f3c0fd273d2c6d9a064f3ae35579b2d244&profile_id=164&oauth2_token_id=57447761',
        features: ['Historic Architecture', 'Cultural Attractions', 'Fine Dining'],
        mustVisit: ['Big Ben', 'Tower Bridge', 'Buckingham Palace'],
        rooms: [
            { type: 'Royal Suite', features: ['City View', 'Butler Service', 'Private Lounge'] },
            { type: 'Executive Room', features: ['Business Center', 'Spa Access', 'Club Lounge'] }
        ]
    },
    'Dubai': {
        image: 'https://images.unsplash.com/photo-1512453979798-5ea266f8880c',
        video: 'https://player.vimeo.com/external/371433846.sd.mp4?s=236da2f3c0fd273d2c6d9a064f3ae35579b2d244&profile_id=164&oauth2_token_id=57447761',
        features: ['Luxury Shopping', 'Desert Adventures', 'Modern Architecture'],
        mustVisit: ['Burj Khalifa', 'Dubai Mall', 'Palm Jumeirah'],
        rooms: [
            { type: 'Panoramic Suite', features: ['Skyline View', 'Private Pool', 'Butler Service'] },
            { type: 'Desert View Room', features: ['Desert View', 'Balcony', 'Spa Access'] }
        ]
    }
};

// Update background image with enhanced transitions
function updateBackgroundImage(location) {
    const data = locationData[location];
    if (data) {
        // Create or get background container
        let backgroundContainer = document.querySelector('.background-container');
        if (!backgroundContainer) {
            backgroundContainer = document.createElement('div');
            backgroundContainer.className = 'background-container';
            document.body.insertBefore(backgroundContainer, document.body.firstChild);
        }

        // Create temporary div for crossfade effect
        const temp = document.createElement('div');
        temp.className = 'absolute inset-0 bg-cover bg-center transition-opacity duration-1000';
        temp.style.backgroundImage = `url(${data.image})`;
        temp.style.opacity = '0';
        backgroundContainer.appendChild(temp);

        // Fade in new background
        requestAnimationFrame(() => {
            temp.style.opacity = '1';
        });

        // Remove old background after transition
        setTimeout(() => {
            const oldBackgrounds = backgroundContainer.querySelectorAll('.absolute.inset-0.bg-cover');
            oldBackgrounds.forEach((bg, index) => {
                if (index < oldBackgrounds.length - 1) {
                    bg.remove();
                }
            });
        }, 1000);
    }
}

// Initialize location autocomplete with enhanced features
function initLocationAutocomplete() {
    const locationInput = document.getElementById('location-input');
    const autocompleteList = document.createElement('ul');
    autocompleteList.className = 'absolute z-10 w-full bg-white shadow-lg rounded-md mt-1 max-h-60 overflow-auto hidden';
    locationInput.parentNode.appendChild(autocompleteList);

    // Add loading indicator
    const loadingIndicator = document.createElement('div');
    loadingIndicator.className = 'absolute right-3 top-1/2 transform -translate-y-1/2 hidden';
    loadingIndicator.innerHTML = `
        <svg class="animate-spin h-5 w-5 text-blue-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
    `;
    locationInput.parentNode.appendChild(loadingIndicator);

    let debounceTimer;
    locationInput.addEventListener('input', (e) => {
        const value = e.target.value.toLowerCase();
        
        // Show loading indicator
        loadingIndicator.classList.remove('hidden');
        
        // Clear previous timer
        clearTimeout(debounceTimer);
        
        // Set new timer
        debounceTimer = setTimeout(() => {
            const matches = Object.keys(locationData).filter(location =>
                location.toLowerCase().includes(value)
            );

            // Update background if exact match is found
            const exactMatch = Object.keys(locationData).find(
                location => location.toLowerCase() === value.toLowerCase()
            );
            if (exactMatch) {
                updateBackgroundImage(exactMatch);
            }

            autocompleteList.innerHTML = '';
            if (matches.length > 0 && value) {
                autocompleteList.classList.remove('hidden');
                matches.forEach(location => {
                    const li = document.createElement('li');
                    li.className = 'px-4 py-2 hover:bg-gray-100 cursor-pointer transition-colors duration-200';
                    
                    // Highlight matching text
                    const regex = new RegExp(`(${value})`, 'gi');
                    const highlightedText = location.replace(regex, '<span class="font-semibold text-blue-600">$1</span>');
                    
                    li.innerHTML = highlightedText;
                    li.addEventListener('click', () => {
                        locationInput.value = location;
                        autocompleteList.classList.add('hidden');
                        updateBackgroundImage(location);
                    });
                    autocompleteList.appendChild(li);
                });
            } else if (value) {
                autocompleteList.classList.remove('hidden');
                autocompleteList.innerHTML = `
                    <li class="px-4 py-2 text-gray-500 italic">
                        No locations found matching "${value}"
                    </li>
                `;
            } else {
                autocompleteList.classList.add('hidden');
            }
            
            // Hide loading indicator
            loadingIndicator.classList.add('hidden');
        }, 300); // Debounce delay
    });

    // Hide autocomplete on click outside
    document.addEventListener('click', (e) => {
        if (!locationInput.contains(e.target)) {
            autocompleteList.classList.add('hidden');
        }
    });

    // Keyboard navigation
    locationInput.addEventListener('keydown', (e) => {
        const items = autocompleteList.querySelectorAll('li');
        const activeItem = autocompleteList.querySelector('li.bg-gray-100');
        
        switch(e.key) {
            case 'ArrowDown':
                e.preventDefault();
                if (!activeItem) {
                    items[0]?.classList.add('bg-gray-100');
                } else {
                    const nextItem = activeItem.nextElementSibling;
                    if (nextItem) {
                        activeItem.classList.remove('bg-gray-100');
                        nextItem.classList.add('bg-gray-100');
                        nextItem.scrollIntoView({ block: 'nearest' });
                    }
                }
                break;
            case 'ArrowUp':
                e.preventDefault();
                if (activeItem) {
                    const prevItem = activeItem.previousElementSibling;
                    if (prevItem) {
                        activeItem.classList.remove('bg-gray-100');
                        prevItem.classList.add('bg-gray-100');
                        prevItem.scrollIntoView({ block: 'nearest' });
                    }
                }
                break;
            case 'Enter':
                if (activeItem) {
                    e.preventDefault();
                    locationInput.value = activeItem.textContent;
                    autocompleteList.classList.add('hidden');
                    updateBackgroundImage(activeItem.textContent);
                }
                break;
            case 'Escape':
                autocompleteList.classList.add('hidden');
                break;
        }
    });
}

// Initialize all enhanced UI features
document.addEventListener('DOMContentLoaded', () => {
    // Initialize location autocomplete
    initLocationAutocomplete();
    
    // Initialize video cards
    initVideoCards();
    
    // Set initial background
    updateBackgroundImage('Maldives');

    // Ensure main content wrapper exists
    let mainContent = document.querySelector('.main-content');
    if (!mainContent) {
        mainContent = document.createElement('div');
        mainContent.className = 'main-content';
        // Wrap existing body content except background
        while (document.body.firstChild) {
            if (!document.body.firstChild.classList?.contains('background-container')) {
                mainContent.appendChild(document.body.firstChild);
            }
        }
        document.body.appendChild(mainContent);
    }
});

// Initialize video cards for featured locations
function initVideoCards() {
    const hotelCards = document.querySelectorAll('.hotel-card');
    
    hotelCards.forEach(card => {
        const location = card.getAttribute('data-location');
        if (locationData[location]) {
            // Create video container
            const videoContainer = document.createElement('div');
            videoContainer.className = 'video-container opacity-0 transition-opacity duration-500';
            
            // Create video element
            const video = document.createElement('video');
            video.className = 'w-full h-full object-cover';
            video.muted = true;
            video.loop = true;
            video.playsInline = true;
            video.src = locationData[location].video;
            
            videoContainer.appendChild(video);
            card.appendChild(videoContainer);
            
            // Add hover events
            card.addEventListener('mouseenter', () => {
                videoContainer.classList.remove('opacity-0');
                video.play().catch(() => {
                    // Handle autoplay restriction gracefully
                    console.log('Video autoplay prevented');
                });
            });
            
            card.addEventListener('mouseleave', () => {
                videoContainer.classList.add('opacity-0');
                setTimeout(() => video.pause(), 500);
            });
            
            // Add click event for location details popup
            card.addEventListener('click', () => {
                showLocationDetails(location);
            });
        }
    });
}

// Initialize and show location details popup
function showLocationDetails(location) {
    const data = locationData[location];
    if (!data) return;
    
    // Create popup container
    const popup = document.createElement('div');
    popup.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 overflow-hidden';
    popup.innerHTML = `
        <div class="bg-white rounded-lg w-[70vw] h-[90vh] relative transform transition-all duration-300 scale-95 opacity-0 flex flex-col">
            <button class="absolute top-4 right-4 text-white hover:text-gray-200 z-10">
                <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                </svg>
            </button>

            <!-- Video Section (60% height) -->
            <div class="relative h-[60%] w-full bg-black">
                <video class="w-full h-full object-cover" autoplay loop muted playsinline>
                    <source src="${data.video}" type="video/mp4">
                </video>
                <div class="absolute inset-0 bg-gradient-to-t from-black to-transparent opacity-60"></div>
                <div class="absolute bottom-0 left-0 right-0 p-8">
                    <h2 class="text-4xl font-bold text-white mb-2">${location}</h2>
                    <p class="text-xl text-white opacity-90">${data.features.join(' • ')}</p>
                </div>
            </div>

            <!-- Scrollable Content (40% height) -->
            <div class="flex-1 overflow-y-auto p-8">
                <!-- Must Visit Places -->
                <div class="mb-8">
                    <h3 class="text-2xl font-bold mb-4">Must Visit Places</h3>
                    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                        ${data.mustVisit.map(place => `
                            <div class="bg-gray-50 rounded-lg p-4 shadow-sm">
                                <h4 class="font-semibold text-lg mb-2">${place}</h4>
                                <p class="text-gray-600">Experience the beauty of ${place} in ${location}</p>
                            </div>
                        `).join('')}
                    </div>
                </div>

                <!-- Available Room Types -->
                <div class="mb-8">
                    <h3 class="text-2xl font-bold mb-4">Luxury Accommodations</h3>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                        ${data.rooms.map(room => `
                            <div class="bg-gray-50 rounded-lg p-6 shadow-sm">
                                <h4 class="text-xl font-semibold mb-3">${room.type}</h4>
                                <ul class="space-y-2">
                                    ${room.features.map(feature => `
                                        <li class="flex items-center text-gray-600">
                                            <svg class="w-5 h-5 mr-2 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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

                <!-- Book Now Button -->
                <div class="flex justify-center">
                    <button class="bg-blue-600 text-white py-4 px-8 rounded-lg hover:bg-blue-700 transition-colors text-lg font-semibold shadow-lg">
                        Book Your Stay at ${location}
                    </button>
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(popup);
    
    // Animate popup entrance
    requestAnimationFrame(() => {
        const content = popup.querySelector('div');
        content.classList.remove('scale-95', 'opacity-0');
    });
    
    // Add close functionality
    const closeButton = popup.querySelector('button');
    const closePopup = () => {
        const content = popup.querySelector('div');
        content.classList.add('scale-95', 'opacity-0');
        setTimeout(() => popup.remove(), 300);
    };
    
    closeButton.addEventListener('click', closePopup);
    popup.addEventListener('click', (e) => {
        if (e.target === popup) closePopup();
    });

    // Start playing video
    const video = popup.querySelector('video');
    video.play().catch(() => {
        // Handle autoplay restrictions gracefully
        console.log('Autoplay prevented');
    });
} 