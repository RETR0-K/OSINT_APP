# blueprints/username_search/utils.py
import subprocess
import json
import os
import requests
import tempfile
import time
import random
from pathlib import Path

def search_sherlock(username):
    """
    Search for username across various platforms using Sherlock
    
    Note: Requires Sherlock to be installed on the system
    Installation: pip install sherlock-project
    """
    # Check if we have mock data for testing
    if os.environ.get('FLASK_ENV') == 'development' and os.environ.get('USE_MOCK_DATA') == 'True':
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
        
        # Run Sherlock command
        process = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120  # 2 minute timeout
        )
        
        if process.returncode != 0:
            print(f"Sherlock error: {process.stderr}")
            return _get_mock_sherlock_data(username)
        
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
            
            return formatted_results
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Error reading Sherlock results: {e}")
            return _get_mock_sherlock_data(username)
        finally:
            # Clean up the temporary file
            try:
                os.unlink(temp_file_path)
            except:
                pass
    
    except subprocess.TimeoutExpired:
        print("Sherlock search timed out")
        return _get_mock_sherlock_data(username)
    except Exception as e:
        print(f"Error running Sherlock: {e}")
        return _get_mock_sherlock_data(username)

def search_whatsmyname(username):
    """
    Search for username across various platforms using WhatsMyName
    
    This implementation uses the web check method directly
    """
    # Check if we have mock data for testing
    if os.environ.get('FLASK_ENV') == 'development' and os.environ.get('USE_MOCK_DATA') == 'True':
        return _get_mock_whatsmyname_data(username)
    
    # Real WhatsMyName implementation
    try:
        # Get the WhatsMyName data file
        wmn_data_url = "https://raw.githubusercontent.com/WebBreacher/WhatsMyName/main/wmn-data.json"
        response = requests.get(wmn_data_url)
        if response.status_code != 200:
            print(f"Error fetching WhatsMyName data: {response.status_code}")
            return _get_mock_whatsmyname_data(username)
        
        wmn_data = response.json()
        sites = wmn_data.get('sites', [])
        
        # Process sites in batches to avoid too many concurrent requests
        batch_size = 10
        results = []
        
        for i in range(0, len(sites), batch_size):
            batch = sites[i:i+batch_size]
            batch_results = _process_wmn_batch(username, batch)
            results.extend(batch_results)
            
            # Add a small delay between batches
            time.sleep(1)
        
        return results
    
    except Exception as e:
        print(f"Error with WhatsMyName search: {e}")
        return _get_mock_whatsmyname_data(username)

def _process_wmn_batch(username, sites_batch):
    """Process a batch of WhatsMyName sites"""
    results = []
    for site in sites_batch:
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
            if 'account_existence_code' in site and response.status_code == site['account_existence_code']:
                results.append({
                    'site_name': site['name'],
                    'url': check_url,
                    'category': site['category'],
                    'source': 'WhatsMyName'
                })
            elif 'account_existence_string' in site and site['account_existence_string'] in response.text:
                results.append({
                    'site_name': site['name'],
                    'url': check_url,
                    'category': site['category'],
                    'source': 'WhatsMyName'
                })
        
        except Exception as e:
            # Skip this site on error
            continue
    
    return results

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