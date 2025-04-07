// Add this to your static/js/main.js file

// Loading overlay functionality
document.addEventListener('DOMContentLoaded', function() {
    // Create loading overlay if it doesn't exist
    if (!document.querySelector('.loading-overlay')) {
        const loadingHTML = `
            <div class="loading-overlay">
                <div class="loading-pulse"></div>
                <div class="loading-spinner"></div>
                <div class="loading-message">Processing your request...</div>
                <div class="loading-details">This may take a few moments while we search multiple sources.</div>
            </div>
        `;
        document.body.insertAdjacentHTML('beforeend', loadingHTML);
    }

    // Get the loading overlay element
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
});