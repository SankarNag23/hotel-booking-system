// Mobile menu functionality
document.addEventListener('DOMContentLoaded', () => {
    const mobileMenuButton = document.querySelector('button[type="button"]');
    const mobileMenu = document.querySelector('.hidden.sm\\:ml-6.sm\\:flex.sm\\:space-x-8');
    
    if (mobileMenuButton && mobileMenu) {
        mobileMenuButton.addEventListener('click', () => {
            mobileMenu.classList.toggle('hidden');
        });
    }

    // Form validation and submission
    const searchForm = document.querySelector('.bg-white.rounded-lg.shadow-xl');
    if (searchForm) {
        searchForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const location = searchForm.querySelector('input[type="text"]').value;
            const checkIn = searchForm.querySelector('input[type="date"]:first-of-type').value;
            const checkOut = searchForm.querySelector('input[type="date"]:last-of-type').value;

            if (!location || !checkIn || !checkOut) {
                alert('Please fill in all fields');
                return;
            }

            if (new Date(checkOut) <= new Date(checkIn)) {
                alert('Check-out date must be after check-in date');
                return;
            }

            // TODO: Implement API call to search hotels
            console.log('Searching hotels:', { location, checkIn, checkOut });
        });
    }

    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Intersection Observer for fade-in animations
    const observerOptions = {
        root: null,
        rootMargin: '0px',
        threshold: 0.1
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('opacity-100', 'translate-y-0');
                entry.target.classList.remove('opacity-0', 'translate-y-4');
            }
        });
    }, observerOptions);

    // Add fade-in animation to elements
    document.querySelectorAll('.group.relative').forEach(el => {
        el.classList.add('transition-all', 'duration-500', 'opacity-0', 'translate-y-4');
        observer.observe(el);
    });
}); 