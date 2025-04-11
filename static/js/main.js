// Main JavaScript functionality for OSINT Tracker

document.addEventListener('DOMContentLoaded', function() {
    // Create loading overlay if it doesn't exist
    const loadingOverlay = document.querySelector('.loading-overlay');
    
    // Function to show loading overlay with custom message
    window.showLoading = function(message, details) {
        const loadingMessage = document.querySelector('.loading-message');
        const loadingDetails = document.querySelector('.loading-details');
        
        if (message && loadingMessage) {
            loadingMessage.textContent = message;
        }
        
        if (details && loadingDetails) {
            loadingDetails.textContent = details;
        }
        
        if (loadingOverlay) {
            loadingOverlay.classList.add('active');
            document.body.style.overflow = 'hidden'; // Prevent scrolling
        }
    };
    
    // Function to hide loading overlay
    window.hideLoading = function() {
        if (loadingOverlay) {
            loadingOverlay.classList.remove('active');
            document.body.style.overflow = ''; // Re-enable scrolling
        }
    };
    
    // Add loading indicator to forms that may take time to process
    const searchForms = document.querySelectorAll('form[data-loading="true"]');
    
    searchForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const message = this.getAttribute('data-loading-message') || 'Processing your request...';
            const details = this.getAttribute('data-loading-details') || 'This may take a few moments while we search multiple sources.';
            
            showLoading(message, details);
        });
    });

    // Handle dropdown menus
    const dropdownButtons = document.querySelectorAll('.dropdown > button');
    dropdownButtons.forEach(button => {
        button.addEventListener('click', function() {
            const dropdownMenu = this.nextElementSibling;
            dropdownMenu.classList.toggle('hidden');
        });
    });

    // Close dropdowns when clicking outside
    document.addEventListener('click', function(event) {
        dropdownButtons.forEach(button => {
            const dropdown = button.parentNode;
            const dropdownMenu = button.nextElementSibling;
            
            if (!dropdown.contains(event.target)) {
                dropdownMenu.classList.add('hidden');
            }
        });
    });

    // Mobile menu toggle
    const mobileMenuButton = document.querySelector('.mobile-menu-button');
    const mobileMenu = document.querySelector('.md\\:hidden');
    
    if (mobileMenuButton && mobileMenu) {
        mobileMenuButton.addEventListener('click', function() {
            mobileMenu.classList.toggle('hidden');
        });
    }

    // Risk gauge animation (if present on page)
    const riskGauges = document.querySelectorAll('.risk-gauge');
    if (riskGauges.length > 0) {
        riskGauges.forEach(gauge => {
            const arc = gauge.querySelector('.risk-gauge-arc');
            const score = parseInt(gauge.getAttribute('data-score') || 0);
            
            if (arc) {
                // Delay to allow CSS transitions to work
                setTimeout(() => {
                    arc.style.strokeDasharray = `${score}, 100`;
                }, 100);
            }
        });
    }
});