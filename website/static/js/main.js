// DriveAhead - Homepage JavaScript
class DriveAheadHomepage {
    constructor() {
        this.init();
    }

    init() {
        console.log('Initializing DriveAhead Homepage...');
        
        // Hide loading screen after content loads
        this.hideLoadingScreen();
        
        // Initialize navigation
        this.initNavigation();
        
        // Initialize hero animations
        this.initAnimations();
        
        console.log('Homepage initialized successfully');
    }

    hideLoadingScreen() {
        const loadingScreen = document.getElementById('loadingScreen');
        if (loadingScreen) {
            // Small delay for smooth transition
            setTimeout(() => {
                loadingScreen.style.opacity = '0';
                setTimeout(() => {
                    loadingScreen.style.display = 'none';
                    console.log('Loading screen hidden successfully');
                }, 500); // Wait for fade transition
            }, 1000);
        }
    }

    initNavigation() {
        // Mobile menu toggle
        const hamburger = document.querySelector('.hamburger');
        const navMenu = document.querySelector('.nav-menu');

        if (hamburger && navMenu) {
            hamburger.addEventListener('click', () => {
                hamburger.classList.toggle('active');
                navMenu.classList.toggle('active');
            });

            // Close menu when clicking on a link
            document.querySelectorAll('.nav-menu a').forEach(link => {
                link.addEventListener('click', () => {
                    hamburger.classList.remove('active');
                    navMenu.classList.remove('active');
                });
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
    }

    initAnimations() {
        // Add scroll-based animations
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-in');
                }
            });
        }, observerOptions);

        // Observe elements for animation
        document.querySelectorAll('.hero-content, .feature-card, .analytics-grid, .cta-section').forEach(el => {
            observer.observe(el);
        });
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new DriveAheadHomepage();
});

// Export for potential module use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = DriveAheadHomepage;
}