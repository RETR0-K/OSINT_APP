// username-search.js - Direct approach without polling
document.addEventListener('DOMContentLoaded', function() {
    const searchForm = document.getElementById('username-search-form');
    
    if (searchForm) {
        searchForm.addEventListener('submit', function(e) {
            e.preventDefault(); // Prevent the default form submission
            
            const username = document.getElementById('username').value;
            if (!username) {
                alert('Please enter a username');
                return;
            }
            
            // Show loading overlay
            window.showLoading('Searching for username...', 'We\'re checking accounts across multiple platforms. This may take a minute or two.');
            
            // Submit form normally, which will redirect to the searching page
            searchForm.submit();
        });
    }
});