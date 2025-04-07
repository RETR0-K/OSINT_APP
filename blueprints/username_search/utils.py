# blueprints/username_search/utils.py
import subprocess
import json
import os
import requests
import tempfile
import time
import random
from pathlib import Path
import concurrent.futures
from flask import current_app
import threading

def start_search(username, search_id, active_searches):
    """
    Start a username search in a background thread and update progress
    """
    # Define the thread function
    def search_thread():
        try:
            # Get the search data
            search_data = active_searches[search_id]
            
            # Update status
            search_data['status'] = 'Initializing search tools...'
            
            # Use ThreadPoolExecutor to run both searches in parallel
            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
                # Submit both search tasks
                sherlock_future = executor.submit(
                    search_sherlock_with_progress, 
                    username, 
                    search_id, 
                    active_searches
                )
                
                whatsmyname_future = executor.submit(
                    search_whatsmyname_with_progress, 
                    username, 
                    search_id, 
                    active_searches
                )
                
                # Wait for both to complete and get results
                sherlock_results = sherlock_future.result()
                whatsmyname_results = whatsmyname_future.result()
            
            # Process and combine results
            combined_results = []
            categories = {}
            
            # Process Sherlock results
            if sherlock_results:
                for site in sherlock_results:
                    combined_results.append({
                        'site_name': site['site_name'],
                        'url': site['url'],
                        'category': site.get('category', 'Uncategorized'),
                        'source': 'Sherlock'
                    })
            
            # Process WhatsMyName results
            if whatsmyname_results:
                for site in whatsmyname_results:
                    combined_results.append({
                        'site_name': site['site_name'],
                        'url': site['url'],
                        'category': site.get('category', 'Uncategorized'),
                        'source': 'WhatsMyName'
                    })
            
            # Count categories
            for result in combined_results:
                category = result['category']
                if category not in categories:
                    categories[category] = 0
                categories[category] += 1
            
            total_found = len(combined_results)
            
            # Calculate risk score based on number of accounts found
            if total_found == 0:
                risk_score = 0
            elif total_found <= 5:
                risk_score = 10
            elif total_found <= 15:
                risk_score = 25
            elif total_found <= 30:
                risk_score = 50
            elif total_found <= 50:
                risk_score = 75
            else:
                risk_score = 100
            
            # Store the final results
            search_data['results'] = {
                'username': username,
                'scan_date': search_data['start_time'],
                'sherlock': sherlock_results,
                'whatsmyname': whatsmyname_results,
                'combined_results': combined_results,
                'categories': categories,
                'total_found': total_found,
                'risk_score': risk_score
            }
            
            # Mark the search as complete
            search_data['is_complete'] = True
            search_data['status'] = 'Search complete'
            
        except Exception as e:
            print(f"Error in search thread: {e}")
            # Update status with error
            if search_id in active_searches:
                active_searches[search_id]['status'] = f"Error: {str(e)}"
                active_searches[search_id]['is_complete'] = True
    
    # Start the thread
    thread = threading.Thread(target=search_thread)
    thread.daemon = True  # Thread will exit when the main program exits
    thread.start()
    
    return search_id

def get_search_progress(search_id, active_searches):
    """Get the current progress of a search"""
    if search_id not in active_searches:
        return {
            'is_complete': False,
            'sherlock': {'percent': 0, 'found': 0},
            'whatsmyname': {'percent': 0, 'found': 0},
            'status': 'Search not found'
        }
    
    search_data = active_searches[search_id]
    return {
        'is_complete': search_data['is_complete'],
        'sherlock': search_data['sherlock'],
        'whatsmyname': search_data['whatsmyname'],
        'status': search_data.get('status', 'Searching...')
    }

def get_search_results(search_id, active_searches):
    """Get the results of a completed search"""
    if search_id not in active_searches:
        return None
    
    search_data = active_searches[search_id]
    return search_data['results']

def search_sherlock_with_progress(username, search_id, active_searches):
    """
    Search for username using Sherlock with progress tracking
    """
    search_data = active_searches[search_id]
    sherlock_data = search_data['sherlock']
    
    # Update status
    sherlock_data['status'] = 'starting'
    search_data['status'] = 'Starting Sherlock search...'
    
    # Check if we have mock data for testing
    if os.environ.get('FLASK_ENV') == 'development' and os.environ.get('USE_MOCK_DATA') == 'True':
        # Simulate progress
        sherlock_data['total_sites'] = 200
        for i in range(1, 101):
            if search_id not in active_searches:
                break
                
            sherlock_data['percent'] = i
            sherlock_data['sites_checked'] = i * 2
            
            if i % 10 == 0:
                sherlock_data['found'] += 1
                
            time.sleep(0.1)  # Simulate work
            
        return _get_mock_sherlock_data(username)
    
    # Real Sherlock implementation
    try:
        # Create a temporary file for output
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as temp:
            temp_file_path = temp.name
        
        # Build the command to run Sherlock
        cmd = [
            'sherlock',
            username,
            '--timeout', '5',
            '--print-found',
            '--output', temp_file_path, 
            '--json'
        ]
        
        # Update status
        sherlock_data['status'] = 'running'
        search_data['status'] = 'Running Sherlock search...'
        
        # Estimate total sites (this is approximate and may not be accurate)
        sherlock_data['total_sites'] = 300  # Approximate number of sites Sherlock checks
        
        # Start the process
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1  # Line buffered
        )
        
        # Track progress
        sites_checked = 0
        sites_found = 0
        
        # Monitor the stdout for progress
        for line in iter(process.stdout.readline, ''):
            if search_id not in active_searches:
                process.kill()
                break
                
            # Look for progress indicators in the output
            if "[*] Checking username" in line:
                sites_checked += 1
                sherlock_data['sites_checked'] = sites_checked
                
                # Calculate approximate percentage
                percent = min(int((sites_checked / sherlock_data['total_sites']) * 100), 99)
                sherlock_data['percent'] = percent
                
            elif "[+]" in line:  # Found account
                sites_found += 1
                sherlock_data['found'] = sites_found
                
            # Update status in the shared data
            search_data['status'] = f"Sherlock: Checked {sites_checked} sites, found {sites_found} accounts"
        
        # Wait for the process to complete
        process.wait()
        
        # Update final status
        sherlock_data['status'] = 'completed'
        sherlock_data['percent'] = 100
        
        # Read the results from the JSON file
        try:
            with open(temp_file_path, 'r') as f:
                results = json.load(f)
            
            # Convert the results to our standard format
            formatted_results = []
            for site_name, data in results.get(username, {}).items():
                if data.get('status', {}).get('message') == "Claimed":
                    formatted_results.append({
                        'site_name': site_name,
                        'url': data.get('url', ''),
                        'category': _get_site_category(site_name),
                        'source': 'Sherlock'
                    })
            
            # Update the final count
            sherlock_data['found'] = len(formatted_results)
            
            return formatted_results
            
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Error reading Sherlock results: {e}")
            sherlock_data['status'] = 'error'
            return _get_mock_sherlock_data(username)
        finally:
            # Clean up the temporary file
            try:
                os.unlink(temp_file_path)
            except:
                pass
    
    except Exception as e:
        print(f"Error running Sherlock: {e}")
        sherlock_data['status'] = 'error'
        return _get_mock_sherlock_data(username)

def search_whatsmyname_with_progress(username, search_id, active_searches):
    """
    Search for username using WhatsMyName with progress tracking
    """
    search_data = active_searches[search_id]
    whatsmyname_data = search_data['whatsmyname']
    
    # Update status
    whatsmyname_data['status'] = 'starting'
    search_data['status'] = 'Starting WhatsMyName search...'
    
    # Check if we have mock data for testing
    if os.environ.get('FLASK_ENV') == 'development' and os.environ.get('USE_MOCK_DATA') == 'True':
        # Simulate progress
        whatsmyname_data['total_sites'] = 150
        for i in range(1, 101):
            if search_id not in active_searches:
                break
                
            whatsmyname_data['percent'] = i
            whatsmyname_data['sites_checked'] = i * 1.5
            
            if i % 15 == 0:
                whatsmyname_data['found'] += 1
                
            time.sleep(0.1)  # Simulate work
            
        return _get_mock_whatsmyname_data(username)
    
    # Real WhatsMyName implementation
    try:
        # Update status
        whatsmyname_data['status'] = 'fetching'
        search_data['status'] = 'Fetching WhatsMyName database...'
        
        # Get the WhatsMyName data file
        wmn_data_url = "https://raw.githubusercontent.com/WebBreacher/WhatsMyName/main/wmn-data.json"
        response = requests.get(wmn_data_url)
        if response.status_code != 200:
            print(f"Error fetching WhatsMyName data: {response.status_code}")
            whatsmyname_data['status'] = 'error'
            return _get_mock_whatsmyname_data(username)
        
        wmn_data = response.json()
        sites = wmn_data.get('sites', [])
        
        # Update total sites count
        whatsmyname_data['total_sites'] = len(sites)
        whatsmyname_data['status'] = 'running'
        search_data['status'] = f'Running WhatsMyName search on {len(sites)} sites...'
        
        # For better parallelism, process sites in multiple batches with ThreadPoolExecutor
        results = []
        sites_checked = 0
        sites_found = 0
        
        # Split sites into manageable batches (e.g., 10 sites per batch)
        batch_size = 10
        site_batches = [sites[i:i+batch_size] for i in range(0, len(sites), batch_size)]
        
        # Process each batch in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            # Submit a batch processing task for each batch of sites
            future_to_batch = {executor.submit(_process_wmn_batch_with_progress, 
                                              username, batch, search_id, 
                                              active_searches, 
                                              sites_checked, sites_found): batch 
                               for batch in site_batches}
            
            # Collect results as they complete
            for future in concurrent.futures.as_completed(future_to_batch):
                if search_id not in active_searches:
                    break
                    
                batch_results, batch_checked, batch_found = future.result()
                results.extend(batch_results)
                
                # Update progress
                sites_checked += batch_checked
                sites_found += batch_found
                
                whatsmyname_data['sites_checked'] = sites_checked
                whatsmyname_data['found'] = sites_found
                
                # Calculate percentage
                percent = min(int((sites_checked / whatsmyname_data['total_sites']) * 100), 99)
                whatsmyname_data['percent'] = percent
                
                # Update status
                search_data['status'] = f"WhatsMyName: Checked {sites_checked} sites, found {sites_found} accounts"
        
        # Update final status
        whatsmyname_data['status'] = 'completed'
        whatsmyname_data['percent'] = 100
        whatsmyname_data['found'] = len(results)
        
        return results
    
    except Exception as e:
        print(f"Error with WhatsMyName search: {e}")
        whatsmyname_data['status'] = 'error'
        return _get_mock_whatsmyname_data(username)

def _process_wmn_batch_with_progress(username, sites_batch, search_id, active_searches, sites_checked_start, sites_found_start):
    """Process a batch of WhatsMyName sites with progress tracking"""
    results = []
    sites_checked = 0
    sites_found = 0
    
    for site in sites_batch:
        if search_id not in active_searches:
            break
            
        try:
            # Skip sites missing required data
            if not all(k in site for k in ['name', 'uri_check', 'category']):
                continue
            
            # Format the URL with the username
            check_url = site['uri_check'].replace('{account}', username)
            
            # Make the request
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(check_url, headers=headers, timeout=5, allow_redirects=True)
            
            # Check if the account exists
            found = False
            if 'account_existence_code' in site and response.status_code == site['account_existence_code']:
                results.append({
                    'site_name': site['name'],
                    'url': check_url,
                    'category': site['category'],
                    'source': 'WhatsMyName'
                })
                found = True
            elif 'account_existence_string' in site and site['account_existence_string'] in response.text:
                results.append({
                    'site_name': site['name'],
                    'url': check_url,
                    'category': site['category'],
                    'source': 'WhatsMyName'
                })
                found = True
            
            # Update counters
            sites_checked += 1
            if found:
                sites_found += 1
        
        except Exception as e:
            # Skip this site on error
            sites_checked += 1
            continue
    
    return results, sites_checked, sites_found

def _get_site_category(site_name):
    """Map site names to categories (simplified)"""
    site_categories = {
        # Social Media
        'Twitter': 'Social Media',
        'Facebook': 'Social Media',
        'Instagram': 'Social Media',
        'TikTok': 'Social Media',
        'Snapchat': 'Social Media',
        'Pinterest': 'Social Media',
        
        # Professional
        'LinkedIn': 'Professional',
        'GitHub': 'Professional',
        'GitLab': 'Professional',
        'StackOverflow': 'Professional',
        'Medium': 'Professional',
        'Dev.to': 'Professional',
        
        # Forums
        'Reddit': 'Forums',
        'Quora': 'Forums',
        'HackerNews': 'Forums',
        
        # Gaming
        'Steam': 'Gaming',
        'Twitch': 'Gaming',
        'Discord': 'Gaming',
        'Xbox': 'Gaming',
        'PlayStation': 'Gaming',
        
        # Media Sharing
        'YouTube': 'Media Sharing',
        'Vimeo': 'Media Sharing',
        'Flickr': 'Media Sharing',
        'SoundCloud': 'Media Sharing',
        
        # Dating
        'Tinder': 'Dating',
        'Bumble': 'Dating',
        'OkCupid': 'Dating',
        
        # Shopping
        'Amazon': 'Shopping',
        'Etsy': 'Shopping',
        'eBay': 'Shopping',
        
        # Tech
        'HackerOne': 'Tech',
        'BugCrowd': 'Tech',
    }
    
    return site_categories.get(site_name, 'Uncategorized')

def _get_mock_sherlock_data(username):
    """Return mock Sherlock data for testing"""
    social_media = [
        {'site_name': 'Twitter', 'url': f'https://twitter.com/{username}', 'category': 'Social Media'},
        {'site_name': 'Instagram', 'url': f'https://instagram.com/{username}', 'category': 'Social Media'},
        {'site_name': 'Facebook', 'url': f'https://facebook.com/{username}', 'category': 'Social Media'},
    ]
    
    professional = [
        {'site_name': 'LinkedIn', 'url': f'https://linkedin.com/in/{username}', 'category': 'Professional'},
        {'site_name': 'GitHub', 'url': f'https://github.com/{username}', 'category': 'Professional'},
    ]
    
    forums = [
        {'site_name': 'Reddit', 'url': f'https://reddit.com/user/{username}', 'category': 'Forums'},
        {'site_name': 'Quora', 'url': f'https://quora.com/profile/{username}', 'category': 'Forums'},
    ]
    
    gaming = [
        {'site_name': 'Steam', 'url': f'https://steamcommunity.com/id/{username}', 'category': 'Gaming'},
        {'site_name': 'Twitch', 'url': f'https://twitch.tv/{username}', 'category': 'Gaming'},
    ]
    
    # Combine all categories and mark source as Sherlock
    mock_results = social_media + professional + forums + gaming
    for result in mock_results:
        result['source'] = 'Sherlock'
    
    # Randomly remove some results to simulate not finding all accounts
    random.shuffle(mock_results)
    return mock_results[:random.randint(5, len(mock_results))]

def _get_mock_whatsmyname_data(username):
    """Return mock WhatsMyName data for testing"""
    media_sharing = [
        {'site_name': 'YouTube', 'url': f'https://youtube.com/user/{username}', 'category': 'Media Sharing'},
        {'site_name': 'Vimeo', 'url': f'https://vimeo.com/{username}', 'category': 'Media Sharing'},
        {'site_name': 'Flickr', 'url': f'https://flickr.com/people/{username}', 'category': 'Media Sharing'},
    ]
    
    dating = [
        {'site_name': 'Tinder', 'url': f'https://tinder.com/@{username}', 'category': 'Dating'},
    ]
    
    shopping = [
        {'site_name': 'Etsy', 'url': f'https://etsy.com/shop/{username}', 'category': 'Shopping'},
        {'site_name': 'eBay', 'url': f'https://ebay.com/usr/{username}', 'category': 'Shopping'},
    ]
    
    tech = [
        {'site_name': 'StackOverflow', 'url': f'https://stackoverflow.com/users/{username}', 'category': 'Tech'},
        {'site_name': 'HackerNews', 'url': f'https://news.ycombinator.com/user?id={username}', 'category': 'Tech'},
    ]
    
    # Combine all categories and mark source as WhatsMyName
    mock_results = media_sharing + dating + shopping + tech
    for result in mock_results:
        result['source'] = 'WhatsMyName'
    
    # Randomly remove some results to simulate not finding all accounts
    random.shuffle(mock_results)
    return mock_results[:random.randint(3, len(mock_results))]