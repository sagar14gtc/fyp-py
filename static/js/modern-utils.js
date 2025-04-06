/**
 * modern-utils.js - Modern UI enhancements
 * Adds interactive features without modifying HTML structure
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize animation on scroll
    initAnimateOnScroll();
    
    // Enhance navbar with scroll effects
    enhanceNavbar();
    
    // Add hover effects to cards
    enhanceCards();
    
    // Add smooth scrolling to anchor links
    initSmoothScroll();
});

/**
 * Initialize animations that trigger when elements come into view
 */
function initAnimateOnScroll() {
    const animatedElements = document.querySelectorAll('.animate-on-scroll, .fade-in, .fade-in-up, .fade-in-down, .fade-in-left, .fade-in-right');
    
    if (animatedElements.length === 0) return;
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.animationPlayState = 'running';
                entry.target.style.opacity = '1';
                observer.unobserve(entry.target);
            }
        });
    }, {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    });
    
    animatedElements.forEach(el => {
        el.style.opacity = '0';
        el.style.animationPlayState = 'paused';
        observer.observe(el);
    });
}

/**
 * Enhance navbar with shadow and background changes on scroll
 */
function enhanceNavbar() {
    const navbar = document.querySelector('.navbar');
    if (!navbar) return;
    
    window.addEventListener('scroll', () => {
        if (window.scrollY > 20) {
            navbar.classList.add('navbar-scrolled');
        } else {
            navbar.classList.remove('navbar-scrolled');
        }
    });
}

/**
 * Add interactive effects to cards on hover
 */
function enhanceCards() {
    // Apply tilt effect to cards
    const cards = document.querySelectorAll('.university-card, .country-card, .testimonial-card');
    
    cards.forEach(card => {
        card.addEventListener('mousemove', function(e) {
            const rect = this.getBoundingClientRect();
            const x = e.clientX - rect.left; // x position within the element
            const y = e.clientY - rect.top;  // y position within the element
            
            const centerX = rect.width / 2;
            const centerY = rect.height / 2;
            
            const deltaX = (x - centerX) / centerX * 5; // max 5deg tilt
            const deltaY = (y - centerY) / centerY * 5;
            
            this.style.transform = `perspective(1000px) rotateX(${-deltaY}deg) rotateY(${deltaX}deg) translateY(-5px)`;
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(-5px)';
            setTimeout(() => {
                this.style.transform = '';
            }, 300);
        });
    });
}

/**
 * Initialize smooth scrolling for anchor links
 */
function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            
            const targetElement = document.querySelector(targetId);
            if (!targetElement) return;
            
            const headerOffset = 80;
            const elementPosition = targetElement.getBoundingClientRect().top;
            const offsetPosition = elementPosition + window.pageYOffset - headerOffset;
            
            window.scrollTo({
                top: offsetPosition,
                behavior: "smooth"
            });
        });
    });
} 