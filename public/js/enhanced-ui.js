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

// Update background image with enhanced transitions
function updateBackgroundImage(location) {
    const data = locationData[location];
    if (data) {
        // Create temporary div for crossfade effect
        const temp = document.createElement('div');
        temp.className = 'fixed inset-0 bg-cover bg-center z-[-1] transition-opacity duration-1000';
        temp.style.backgroundImage = `url(${data.image})`;
        temp.style.opacity = '0';
        document.body.appendChild(temp);

        // Fade in new background
        setTimeout(() => {
            temp.style.opacity = '1';
        }, 50);

        // Remove old background after transition
        setTimeout(() => {
            const oldBackgrounds = document.querySelectorAll('.fixed.inset-0.bg-cover');
            oldBackgrounds.forEach((bg, index) => {
                if (index < oldBackgrounds.length - 1) {
                    bg.remove();
                }
            });
        }, 1000);
    }
}

// Convert featured hotel cards to video cards with enhanced loading
function initVideoCards() {
    const hotelCards = document.querySelectorAll('.hotel-card');
    hotelCards.forEach(card => {
        const location = card.querySelector('h3').textContent.trim();
        const data = locationData[location];
        if (data) {
            // Create video container with loading state
            const imgContainer = card.querySelector('.aspect-w-1');
            const videoContainer = document.createElement('div');
            videoContainer.className = 'relative w-full h-full';
            
            // Add loading spinner
            const spinner = document.createElement('div');
            spinner.className = 'absolute inset-0 flex items-center justify-center bg-gray-100';
            spinner.innerHTML = `
                <svg class="animate-spin h-8 w-8 text-blue-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
            `;
            
            // Create and configure video element
            const video = document.createElement('video');
            video.className = 'w-full h-full object-cover opacity-0 transition-opacity duration-500';
            video.loop = true;
            video.muted = true;
            video.playsInline = true;
            video.src = data.video;
            
            // Handle video loading
            video.addEventListener('loadeddata', () => {
                video.play().then(() => {
                    spinner.remove();
                    video.style.opacity = '1';
                }).catch(console.error);
            });
            
            // Add fallback for video error
            video.addEventListener('error', () => {
                const fallbackImg = document.createElement('img');
                fallbackImg.src = data.image;
                fallbackImg.className = 'w-full h-full object-cover';
                videoContainer.innerHTML = '';
                videoContainer.appendChild(fallbackImg);
            });
            
            // Assemble video container
            videoContainer.appendChild(spinner);
            videoContainer.appendChild(video);
            imgContainer.innerHTML = '';
            imgContainer.appendChild(videoContainer);

            // Add hover effect for video controls
            const controls = document.createElement('div');
            controls.className = 'absolute inset-0 bg-black bg-opacity-0 hover:bg-opacity-20 transition-opacity duration-200 flex items-center justify-center opacity-0 hover:opacity-100';
            controls.innerHTML = `
                <button class="p-2 bg-white rounded-full shadow-lg transform hover:scale-110 transition-transform duration-200">
                    <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                    </svg>
                </button>
            `;
            videoContainer.appendChild(controls);

            // Add click handler for details popup
            controls.addEventListener('click', (e) => {
                e.stopPropagation();
                showLocationDetails(location);
            });
        }
    });
}

// Show location details popup with enhanced animations
function showLocationDetails(location) {
    const data = locationData[location];
    if (!data) return;

    const popup = document.createElement('div');
    popup.className = 'fixed inset-0 bg-black bg-opacity-0 flex items-center justify-center z-50 opacity-0 transition-all duration-300';
    popup.innerHTML = `
        <div class="bg-white rounded-lg p-8 max-w-2xl w-full mx-4 max-h-90vh overflow-auto transform translate-y-4 transition-transform duration-300">
            <div class="flex justify-between items-start">
                <h2 class="text-2xl font-bold mb-4">${location}</h2>
                <button class="text-gray-500 hover:text-gray-700 transition-colors duration-200" onclick="this.closest('.fixed').remove()">
                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                </button>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                    <h3 class="font-bold mb-2">Features</h3>
                    <ul class="list-disc pl-5 mb-4 space-y-2">
                        ${data.features.map(f => `<li class="text-gray-700">${f}</li>`).join('')}
                    </ul>
                    <h3 class="font-bold mb-2">Must Visit</h3>
                    <ul class="list-disc pl-5 space-y-2">
                        ${data.mustVisit.map(m => `<li class="text-gray-700">${m}</li>`).join('')}
                    </ul>
                </div>
                <div>
                    <h3 class="font-bold mb-2">Available Rooms</h3>
                    ${data.rooms.map(room => `
                        <div class="mb-4 p-4 bg-gray-50 rounded-lg">
                            <h4 class="font-semibold text-blue-600">${room.type}</h4>
                            <ul class="list-disc pl-5 mt-2 space-y-1">
                                ${room.features.map(f => `<li class="text-gray-700">${f}</li>`).join('')}
                            </ul>
                        </div>
                    `).join('')}
                </div>
            </div>
        </div>
    `;
    document.body.appendChild(popup);

    // Trigger animations
    requestAnimationFrame(() => {
        popup.style.backgroundColor = 'rgba(0, 0, 0, 0.5)';
        popup.style.opacity = '1';
        popup.querySelector('.transform').style.transform = 'translateY(0)';
    });

    // Add close on escape key
    const handleEscape = (e) => {
        if (e.key === 'Escape') {
            popup.remove();
            document.removeEventListener('keydown', handleEscape);
        }
    };
    document.addEventListener('keydown', handleEscape);

    // Add close on background click
    popup.addEventListener('click', (e) => {
        if (e.target === popup) {
            popup.remove();
        }
    });
}

// Initialize enhanced UI features
document.addEventListener('DOMContentLoaded', () => {
    initLocationAutocomplete();
    initVideoCards();
}); 