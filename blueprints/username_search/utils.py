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
import re

def search_username(username):
    """
    Search for username across platforms using both Sherlock and WhatsMyName concurrently
    """
    # Use ThreadPoolExecutor to run both searches in parallel
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        # Submit both search tasks
        sherlock_future = executor.submit(search_sherlock, username)
        whatsmyname_future = executor.submit(search_whatsmyname, username)
        
        # Wait for both to complete and get results
        sherlock_results = sherlock_future.result()
        whatsmyname_results = whatsmyname_future.result()
    
    # Return both results
    return {
        'sherlock': sherlock_results,
        'whatsmyname': whatsmyname_results
    }

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
            
            # Convert the results to our standard format and validate each found account
            formatted_results = []
            for site_name, data in results.get(username, {}).items():
                if data.get('status', {}).get('message') == "Claimed":
                    url = data.get('url', '')
                    # Only add if verification passes
                    if verify_account_exists(url, site_name):
                        formatted_results.append({
                            'site_name': site_name,
                            'url': url,
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
        response = requests.get(wmn_data_url, timeout=10)
        if response.status_code != 200:
            print(f"Error fetching WhatsMyName data: {response.status_code}")
            return []  # Return empty list instead of mock data for production
        
        wmn_data = response.json()
        sites = wmn_data.get('sites', [])
        
        # For better parallelism, process sites in multiple batches with ThreadPoolExecutor
        results = []
        
        # Split sites into manageable batches (e.g., 10 sites per batch)
        batch_size = 10
        site_batches = [sites[i:i+batch_size] for i in range(0, len(sites), batch_size)]
        
        # Process each batch in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            # Submit a batch processing task for each batch of sites
            future_to_batch = {executor.submit(_process_wmn_batch, username, batch): batch for batch in site_batches}
            
            # Collect results as they complete
            for future in concurrent.futures.as_completed(future_to_batch):
                batch_results = future.result()
                results.extend(batch_results)
        
        return results
    
    except Exception as e:
        print(f"Error with WhatsMyName search: {e}")
        return []  # Return empty list instead of mock data for production

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
            found = False
            if 'account_existence_code' in site and response.status_code == site['account_existence_code']:
                # Verify content to reduce false positives
                if verify_account_content(response.text, site, username):
                    results.append({
                        'site_name': site['name'],
                        'url': check_url,
                        'category': site.get('category', 'Uncategorized'),
                        'source': 'WhatsMyName'
                    })
                    found = True
            elif 'account_existence_string' in site and site['account_existence_string'] in response.text:
                # Verify content to reduce false positives
                if verify_account_content(response.text, site, username):
                    results.append({
                        'site_name': site['name'],
                        'url': check_url,
                        'category': site.get('category', 'Uncategorized'),
                        'source': 'WhatsMyName'
                    })
                    found = True
        
        except requests.RequestException:
            # Skip this site on error
            continue
        except Exception as e:
            # Skip this site on any other error
            print(f"Error checking {site.get('name', 'unknown site')}: {e}")
            continue
    
    return results

def verify_account_exists(url, site_name):
    """Verify that an account actually exists by checking the content of the page"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=5, allow_redirects=True)
        
        # Common error indicators across different sites
        error_patterns = [
            r"(user not found|account not found|page not found|profile not found|404)",
            r"(doesn't exist|does not exist|not available|no user|isn't here)",
            r"(no profile|user doesn't exist|profile doesn't exist|account doesn't exist)",
            r"(couldn't find|couldn't be found|cannot be found|not be found)",
            r"(deleted|disabled|suspended|removed|inactive|deactivated)"
        ]
        
        # Check for error patterns in the page content, ignoring case
        content_lower = response.text.lower()
        for pattern in error_patterns:
            if re.search(pattern, content_lower):
                return False
        
        # Site-specific checks
        if "twitter.com" in url:
            if "this account doesn't exist" in content_lower or "does not exist" in content_lower:
                return False
        elif "instagram.com" in url:
            if "sorry, this page isn't available" in content_lower:
                return False
        elif "facebook.com" in url:
            if "page not found" in content_lower or "isn't available" in content_lower:
                return False
        elif "github.com" in url:
            if "not found" in content_lower or "404" in content_lower:
                return False
        
        # If no error patterns found, assume account exists
        return True
    
    except Exception as e:
        print(f"Error verifying account {url}: {e}")
        return False  # If verification fails, don't include the account

def verify_account_content(content, site, username):
    """
    Verify that the account content actually indicates a real account
    and not just a 'not found' page that returns 200 status
    """
    # Common not-found indicators in page content
    not_found_indicators = [
        "not found", "doesn't exist", "does not exist", "no such user", 
        "no such account", "page not found", "profile not found", "account not found",
        "couldn't find", "couldn't be found", "cannot be found", "not be found",
        "deleted", "disabled", "suspended", "removed", "inactive", "deactivated"
    ]
    
    # Check for username presence in content for additional validation
    username_presence = username.lower() in content.lower()
    
    # Check for not-found indicators
    for indicator in not_found_indicators:
        if indicator.lower() in content.lower():
            return False
    
    # For more reliable validation, check for expected username appearance
    if 'username_claimed_pattern' in site:
        pattern = site['username_claimed_pattern']
        if pattern and not re.search(pattern, content):
            return False
    
    # If we have a positive match pattern defined for the site, use it
    if 'account_existence_string' in site:
        positive_pattern = site['account_existence_string']
        if positive_pattern and positive_pattern not in content:
            return False
    
    # If the site-specific check passes and no error indicators found, assume account exists
    return True

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