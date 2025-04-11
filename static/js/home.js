// static/js/home.js
document.addEventListener('DOMContentLoaded', function() {
    // Handle Email Breach Check form
    const emailBreachForm = document.getElementById('email-breach-form');
    if (emailBreachForm) {
        emailBreachForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const email = document.getElementById('email-input').value.trim();
            if (!email) {
                alert('Please enter an email address');
                return;
            }
            
            // Show loading animation
            window.showLoading('Checking data breaches...', 'We\'re searching multiple data breach databases. This may take a few moments.');
            
            // Submit form
            this.submit();
        });
    }
    
    // Handle Username Lookup form
    const usernameLookupForm = document.getElementById('username-lookup-form');
    if (usernameLookupForm) {
        usernameLookupForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const username = document.getElementById('username-input').value.trim();
            if (!username) {
                alert('Please enter a username');
                return;
            }
            
            // Show loading animation
            window.showLoading('Searching accounts for this username...', 'We\'re checking hundreds of platforms using Sherlock and WhatsMyName. This may take up to a minute.');
            
            // Submit form
            this.submit();
        });
    }
    
    // Handle AI Analysis button
    const aiAnalysisBtn = document.getElementById('run-ai-analysis-btn');
    if (aiAnalysisBtn) {
        aiAnalysisBtn.addEventListener('click', function() {
            window.location.href = aiAnalysisBtn.getAttribute('data-url');
        });
    }
});