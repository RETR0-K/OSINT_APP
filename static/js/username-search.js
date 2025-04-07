document.addEventListener('DOMContentLoaded', function() {
    const searchForm = document.getElementById('username-search-form');
    const progressContainer = document.getElementById('search-progress-container');
    const sherlockProgress = document.getElementById('sherlock-progress');
    const whatsmynameProgress = document.getElementById('whatsmyname-progress');
    const sherlockCounter = document.getElementById('sherlock-counter');
    const whatsmynameCounter = document.getElementById('whatsmyname-counter');
    const searchStatusText = document.getElementById('search-status-text');
    
    if (searchForm) {
        searchForm.addEventListener('submit', function(e) {
            e.preventDefault(); // Prevent the default form submission
            
            const username = document.getElementById('username').value;
            if (!username) {
                alert('Please enter a username');
                return;
            }
            
            // Show the progress container
            progressContainer.classList.remove('hidden');
            
            // Reset progress bars and counters
            sherlockProgress.style.width = '0%';
            whatsmynameProgress.style.width = '0%';
            sherlockCounter.textContent = '0 accounts found';
            whatsmynameCounter.textContent = '0 accounts found';
            searchStatusText.textContent = 'Starting search...';
            
            // Start the progress monitoring
            monitorProgress(username);
            
            // Submit the actual search request
            fetch('/username-search/search-start', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: new URLSearchParams({
                    'username': username,
                })
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Search failed');
                }
                return response.json();
            })
            .then(data => {
                if (data.search_id) {
                    // Store the search ID for progress polling
                    window.currentSearchId = data.search_id;
                } else {
                    throw new Error('No search ID received');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                searchStatusText.textContent = 'Error starting search: ' + error.message;
            });
        });
    }
    
    function monitorProgress(username) {
        let pollCount = 0;
        let isComplete = false;
        
        const pollProgress = function() {
            if (isComplete || pollCount > 120) { // Stop after 2 minutes (120 * 1s)
                return;
            }
            
            pollCount++;
            
            fetch('/username-search/search-progress', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: new URLSearchParams({
                    'username': username,
                    'search_id': window.currentSearchId || ''
                })
            })
            .then(response => response.json())
            .then(data => {
                // Update progress based on the response
                if (data.sherlock) {
                    const sherlockPercent = data.sherlock.percent || 0;
                    sherlockProgress.style.width = `${sherlockPercent}%`;
                    sherlockCounter.textContent = `${data.sherlock.found || 0} accounts found`;
                }
                
                if (data.whatsmyname) {
                    const whatsmynamePercent = data.whatsmyname.percent || 0;
                    whatsmynameProgress.style.width = `${whatsmynamePercent}%`;
                    whatsmynameCounter.textContent = `${data.whatsmyname.found || 0} accounts found`;
                }
                
                // Update status text
                searchStatusText.textContent = data.status || 'Searching...';
                
                // Check if search is complete
                if (data.is_complete) {
                    isComplete = true;
                    // Redirect to results page
                    window.location.href = `/username-search/results/${window.currentSearchId}`;
                } else {
                    // Continue polling
                    setTimeout(pollProgress, 1000); // Poll every 1 second
                }
            })
            .catch(error => {
                console.error('Error:', error);
                searchStatusText.textContent = 'Error monitoring progress: ' + error.message;
                // Continue polling despite errors
                setTimeout(pollProgress, 1000);
            });
        };
        
        // Start polling
        pollProgress();
    }
});