document.addEventListener('DOMContentLoaded', function() {
    // Animation on scroll
    const animateElements = document.querySelectorAll('.animate-on-scroll');
    
    // Initial check for elements in viewport on page load
    checkAnimations();
    
    // Check animation elements when scrolling
    window.addEventListener('scroll', checkAnimations);
    
    function checkAnimations() {
        animateElements.forEach(element => {
            const elementTop = element.getBoundingClientRect().top;
            const elementVisible = 150; // How far from the bottom of the viewport to start the animation
            
            // Check if element is in viewport
            if (elementTop < window.innerHeight - elementVisible) {
                // Get delay from data attribute or default to 0
                const delay = element.dataset.delay || 0;
                
                // Apply delay and add visible class
                setTimeout(() => {
                    element.classList.add('visible');
                }, delay);
            }
        });
    }
    
    // Tooltip initialization for Bootstrap
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
    
    // Flash message auto-dismiss after 5 seconds
    const alertMessages = document.querySelectorAll('.alert');
    alertMessages.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
});
