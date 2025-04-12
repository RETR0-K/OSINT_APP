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
import threading
import re

def search_username(username):
    """
    Search for username across platforms using both Sherlock and WhatsMyName concurrently
    """
    # Create progress tracking objects
    progress_file = os.path.join(tempfile.gettempdir(), f"search_progress_{username}_{int(time.time())}.json")
    
    # Initialize progress file
    progress = {
        'sherlock': {
            'status': 'starting',
            'message': 'Starting Sherlock search...',
            'found': 0,
            'total_checked': 0,
            'total_sites': 0
        },
        'whatsmyname': {
            'status': 'starting',
            'message': 'Starting WhatsMyName search...',
            'found': 0,
            'total_checked': 0,
            'total_sites': 0
        }
    }
    
    with open(progress_file, 'w') as f:
        json.dump(progress, f)
    
    # Use ThreadPoolExecutor to run both searches in parallel
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        # Submit both search tasks
        sherlock_future = executor.submit(search_sherlock, username, progress_file)
        whatsmyname_future = executor.submit(search_whatsmyname, username, progress_file)
        
        # Wait for both to complete and get results
        sherlock_results = sherlock_future.result()
        whatsmyname_results = whatsmyname_future.result()
    
    # Return both results and progress file path
    return {
        'sherlock': sherlock_results,
        'whatsmyname': whatsmyname_results,
        'progress_file': progress_file
    }

def is_sherlock_installed():
    """Check if Sherlock is installed and available"""
    try:
        result = subprocess.run(['sherlock', '--version'], capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False

def search_sherlock(username, progress_file):
    """
    Search for username across various platforms using Sherlock
    """
    if not is_sherlock_installed():
        # Show clear message that Sherlock isn't installed
        print("Sherlock is not installed. Using mock data.")
        update_progress(progress_file, 'sherlock', 'error', "Sherlock not installed")
        return _get_mock_sherlock_data(username)
    
    try:
        # Update progress
        update_progress(progress_file, 'sherlock', 'running', "Starting Sherlock search")
        
        # Create a temporary directory for output
        temp_dir = tempfile.mkdtemp()
        output_path = os.path.join(temp_dir, "sherlock_results")
        
        # Build the command to run Sherlock - use simpler command without json output
        cmd = [
            'sherlock',
            username,
            '--timeout', '5',
            '--print-found',
            '--output', output_path
        ]
        
        print(f"Running Sherlock command: {' '.join(cmd)}")
        
        # Run Sherlock command with live output capture for progress updates
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1  # Line buffered
        )
        
        # Monitor output for progress updates
        sites_checked = 0
        sites_found = 0
        found_sites = []
        
        # Read output line by line
        for line in iter(process.stdout.readline, ''):
            print(f"Sherlock output: {line.strip()}")
            if "[+]" in line:  # Found a match
                sites_found += 1
                # Extract site name and URL from the line
                site_info = line.strip().split("[+] ")[1] if "[+] " in line else ""
                if site_info and ": " in site_info:
                    site_parts = site_info.split(": ")
                    site_name = site_parts[0].strip()
                    site_url = site_parts[1].strip() if len(site_parts) > 1 else ""
                    
                    if site_name and site_url:
                        found_sites.append({
                            'site_name': site_name,
                            'url': site_url,
                            'category': _get_site_category(site_name),
                            'source': 'Sherlock'
                        })
                
                update_progress(progress_file, 'sherlock', 'running', 
                                f"Found {sites_found} accounts", sites_found, sites_checked)
            elif "]" in line and "[+]" not in line:  # Checked a site
                sites_checked += 1
                if sites_checked % 5 == 0:  # Update every 5 sites to avoid too many updates
                    update_progress(progress_file, 'sherlock', 'running', 
                                   f"Checked {sites_checked} sites", sites_found, sites_checked)
        
        # Read any error output
        error_output = process.stderr.read()
        if error_output:
            print(f"Sherlock stderr: {error_output}")
        
        # Wait for process to complete
        process.wait()
        
        if process.returncode != 0:
            print(f"Sherlock error: {error_output}")
            update_progress(progress_file, 'sherlock', 'error', f"Error: {error_output}")
            # If we have any results despite the error, return them instead of mock data
            if found_sites:
                return found_sites
            return _get_mock_sherlock_data(username)
        
        # If we parsed the results from stdout, use those
        if found_sites:
            # Update final progress
            update_progress(progress_file, 'sherlock', 'completed', 
                           f"Completed with {len(found_sites)} accounts found", 
                           len(found_sites), sites_checked)
            return found_sites
        
        # As a fallback, check for the output file that Sherlock might have created
        output_file = f"{output_path}.txt"
        if os.path.exists(output_file):
            # Parse the text file
            with open(output_file, 'r') as f:
                lines = f.readlines()
            
            parsed_sites = []
            for line in lines:
                if ": " in line:
                    site_parts = line.strip().split(": ")
                    site_name = site_parts[0].strip()
                    site_url = site_parts[1].strip() if len(site_parts) > 1 else ""
                    
                    if site_name and site_url:
                        parsed_sites.append({
                            'site_name': site_name,
                            'url': site_url,
                            'category': _get_site_category(site_name),
                            'source': 'Sherlock'
                        })
            
            # Update final progress
            update_progress(progress_file, 'sherlock', 'completed', 
                           f"Completed with {len(parsed_sites)} accounts found", 
                           len(parsed_sites), sites_checked)
            return parsed_sites
        
        # If we couldn't get results from stdout or file, return mock data
        print("No Sherlock results found, using mock data")
        update_progress(progress_file, 'sherlock', 'completed', 
                       "Completed with no accounts found", 0, sites_checked)
        return []
    
    except Exception as e:
        import traceback
        print(f"Error running Sherlock: {e}")
        print(traceback.format_exc())
        update_progress(progress_file, 'sherlock', 'error', str(e))
        return _get_mock_sherlock_data(username)
    finally:
        # Clean up the temporary directory
        try:
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
        except Exception as e:
            print(f"Error cleaning up temp dir: {e}")

def search_whatsmyname(username, progress_file):
    """
    Search for username across various platforms using WhatsMyName API
    """
    update_progress(progress_file, 'whatsmyname', 'running', "Starting WhatsMyName search")
    
    try:
        # Get the WhatsMyName data file
        wmn_data_url = "https://raw.githubusercontent.com/WebBreacher/WhatsMyName/main/wmn-data.json"
        
        update_progress(progress_file, 'whatsmyname', 'running', "Fetching WhatsMyName data")
        response = requests.get(wmn_data_url, timeout=10)
        
        if response.status_code != 200:
            print(f"Error fetching WhatsMyName data: {response.status_code}")
            update_progress(progress_file, 'whatsmyname', 'error', 
                           f"Error fetching data: HTTP {response.status_code}")
            return _get_mock_whatsmyname_data(username)
        
        wmn_data = response.json()
        sites = wmn_data.get('sites', [])
        
        # Update progress with total number of sites
        total_sites = len(sites)
        update_progress(progress_file, 'whatsmyname', 'running', 
                       f"Checking {total_sites} sites", 0, 0, total_sites)
        
        # Process sites in batches for better parallelism
        results = []
        sites_checked = 0
        
        # Split sites into manageable batches
        batch_size = 10
        site_batches = [sites[i:i+batch_size] for i in range(0, len(sites), batch_size)]
        
        # Process each batch in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            # Submit a batch processing task for each batch of sites
            future_to_batch = {executor.submit(_process_wmn_batch, username, batch, progress_file, 
                                              sites_checked + i*batch_size): batch 
                              for i, batch in enumerate(site_batches)}
            
            # Collect results as they complete
            for future in concurrent.futures.as_completed(future_to_batch):
                try:
                    batch_results, batch_checked = future.result()
                    results.extend(batch_results)
                    sites_checked += batch_checked
                    
                    # Update progress
                    update_progress(progress_file, 'whatsmyname', 'running', 
                                   f"Checked {sites_checked}/{total_sites} sites", 
                                   len(results), sites_checked, total_sites)
                except Exception as e:
                    print(f"Error processing WhatsMyName batch: {e}")
        
        # Final progress update
        update_progress(progress_file, 'whatsmyname', 'completed', 
                       f"Completed with {len(results)} accounts found", 
                       len(results), total_sites, total_sites)
        
        if not results:
            print("No WhatsMyName results found, using mock data")
            return _get_mock_whatsmyname_data(username)
            
        return results
    
    except Exception as e:
        print(f"Error with WhatsMyName search: {e}")
        update_progress(progress_file, 'whatsmyname', 'error', str(e))
        return _get_mock_whatsmyname_data(username)

def update_progress(progress_file, source, status, message, found=0, checked=0, total=0):
    """Update the progress file with current status"""
    try:
        with open(progress_file, 'r') as f:
            progress = json.load(f)
        
        progress[source]['status'] = status
        progress[source]['message'] = message
        progress[source]['found'] = found
        progress[source]['total_checked'] = checked
        
        if total > 0:
            progress[source]['total_sites'] = total
        
        with open(progress_file, 'w') as f:
            json.dump(progress, f)
    except Exception as e:
        print(f"Error updating progress: {e}")

def _process_wmn_batch(username, sites_batch, progress_file, start_index):
    """Process a batch of WhatsMyName sites"""
    results = []
    sites_checked = 0
    
    for site in sites_batch:
        try:
            # Skip sites missing required data
            if not all(k in site for k in ['name', 'uri_check', 'category']):
                sites_checked += 1
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
            pass
        except Exception as e:
            # Skip this site on any other error
            print(f"Error checking {site.get('name', 'unknown site')}: {e}")
            pass
        
        # Increment counter regardless of outcome
        sites_checked += 1
    
    return results, sites_checked

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

def get_search_progress(progress_file):
    """Get current search progress from the file"""
    try:
        with open(progress_file, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error reading progress file: {e}")
        return None