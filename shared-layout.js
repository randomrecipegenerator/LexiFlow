document.addEventListener('DOMContentLoaded', function() {
    console.log('LexiFlow Layout initialized');
    
    // Mobile Menu Toggle
    const toggle = document.querySelector('.nav-toggle');
    
    if (toggle) {
        toggle.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            // Find the nav links - look for ID or Class
            const navLinks = document.getElementById('navLinks') || document.querySelector('.nav-links');
            
            if (navLinks) {
                navLinks.classList.toggle('active');
                console.log('Mobile menu toggled. Active:', navLinks.classList.contains('active'));
                
                // Toggle button text or icon if needed
                // toggle.textContent = navLinks.classList.contains('active') ? '✕' : '☰';
            } else {
                console.error('Could not find nav-links element');
            }
        });
    }

    // Close menu when clicking outside
    document.addEventListener('click', function(e) {
        const navLinks = document.getElementById('navLinks') || document.querySelector('.nav-links');
        const toggle = document.querySelector('.nav-toggle');
        
        if (navLinks && navLinks.classList.contains('active')) {
            if (!navLinks.contains(e.target) && !toggle.contains(e.target)) {
                navLinks.classList.remove('active');
                console.log('Mobile menu closed (clicked outside)');
            }
        }
    });

    // Close menu on resize if moving to desktop
    window.addEventListener('resize', function() {
        if (window.innerWidth > 768) {
            const navLinks = document.getElementById('navLinks') || document.querySelector('.nav-links');
            if (navLinks && navLinks.classList.contains('active')) {
                navLinks.classList.remove('active');
            }
        }
    });
});
