# blueprints/data_breach/utils.py
import requests
import json
import hashlib
import time

def check_breach_directory(email, api_key):
    """
    Check if an email has been compromised using the BreachDirectory API via RapidAPI
    """
    if not api_key:
        # Return example data for development without API key
        return [
            {
                'source': 'Adobe',
                'password': '******ed2',
                'last_breach': '2013-10-04'
            }
        ]
    
    url = "https://breachdirectory.p.rapidapi.com/"
    querystring = {"func": "auto", "term": email}
    headers = {
        'x-rapidapi-key': api_key,
        'x-rapidapi-host': "breachdirectory.p.rapidapi.com"
    }
    
    try:
        response = requests.get(url, headers=headers, params=querystring)
        if response.status_code == 200:
            data = response.json()
            # Format the response to match our expected structure
            breaches = []
            for result in data.get('result', []):
                breaches.append({
                    'source': result.get('sources', ['Unknown'])[0],
                    'password': result.get('password', '********'),
                    'last_breach': result.get('last_breach', 'Unknown'),
                    'hash': result.get('hash', ''),
                    'sha1': result.get('sha1', ''),
                    'hash_password': result.get('hash_password', False)
                })
            return breaches
        elif response.status_code == 429:
            # Rate limited, wait and try again
            print("Rate limited by BreachDirectory API. Waiting 2 seconds...")
            time.sleep(2)
            return check_breach_directory(email, api_key)
        else:
            print(f"Error checking BreachDirectory: {response.status_code}")
            return None
    except Exception as e:
        print(f"Exception checking BreachDirectory: {e}")
        return None

def check_breach_search(email, api_key):
    """
    Check if an email has been compromised using the BreachSearch API via RapidAPI
    """
    if not api_key:
        # Return example data for development without API key
        return [
            {
                'database_name': {
                    'info_leak': 'Description of the leak',
                    'data': [
                        {
                            'email': email,
                            'first_name': 'John',
                            'last_name': 'Doe'
                        }
                    ]
                }
            }
        ]
    
    url = f"https://breachsearch.p.rapidapi.com/dafney47@gmail.com"
    url = url.replace('dafney47@gmail.com', email)  # Replace with the actual email
    
    headers = {
        'x-rapidapi-key': api_key,
        'x-rapidapi-host': "breachsearch.p.rapidapi.com"
    }
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            # Format the response to match our expected structure
            breaches = []
            
            # Process the results based on the structure shown in the screenshots
            database_list = data.get('List', [])
            for database in database_list:
                for db_name, db_info in database.items():
                    if db_name == 'DatabaseName':
                        info_leak = db_info.get('InfoLeak', 'Unknown breach')
                        breach_data = db_info.get('Data', [])
                        
                        for record in breach_data:
                            breaches.append({
                                'source': db_name,
                                'description': info_leak,
                                'email': record.get('Email', email),
                                'first_name': record.get('FirstName', ''),
                                'last_name': record.get('LastName', '')
                            })
            
            return breaches
        elif response.status_code == 429:
            # Rate limited, wait and try again
            print("Rate limited by BreachSearch API. Waiting 2 seconds...")
            time.sleep(2)
            return check_breach_search(email, api_key)
        else:
            print(f"Error checking BreachSearch: {response.status_code}")
            return None
    except Exception as e:
        print(f"Exception checking BreachSearch: {e}")
        return None

def check_osint_search(email, api_key):
    """
    Check if an email has been compromised using the OSINT Search API via RapidAPI
    """
    if not api_key:
        # Return example data for development without API key
        return {
            'success': True,
            'found': 2,
            'result': [
                {
                    'email': email,
                    'hash_password': True,
                    'password': '********',
                    'sha1': '44fc217f321150e797486c6838d2579ae4af31e',
                    'hash': 'd5K83+4xxgBwNbWH2Yfb3FZK35GXM/gocuT8r9gPFCQN/V',
                    'sources': ['Unknown']
                }
            ]
        }
    
    url = "https://osint-phone-email-names-search-everything.p.rapidapi.com/search"
    
    payload = {
        "request": email,
        "lang": "en"
    }
    
    headers = {
        'x-rapidapi-key': api_key,
        'x-rapidapi-host': "osint-phone-email-names-search-everything.p.rapidapi.com",
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            data = response.json()
            # Format the response to match our expected structure
            breaches = []
            
            # Process each result item
            for result_item in data.get('result', []):
                # Only include records where the email matches
                if 'email' in result_item and result_item['email'] == email:
                    source = 'Unknown'
                    if 'sources' in result_item and len(result_item['sources']) > 0:
                        source = result_item['sources'][0]
                    
                    breaches.append({
                        'source': source,
                        'password': result_item.get('password', '********'),
                        'hash': result_item.get('hash', ''),
                        'sha1': result_item.get('sha1', ''),
                        'hash_password': result_item.get('hash_password', False)
                    })
            
            return {
                'found': data.get('found', 0),
                'breaches': breaches
            }
        elif response.status_code == 429:
            # Rate limited, wait and try again
            print("Rate limited by OSINT Search API. Waiting 2 seconds...")
            time.sleep(2)
            return check_osint_search(email, api_key)
        else:
            print(f"Error checking OSINT Search: {response.status_code}")
            return None
    except Exception as e:
        print(f"Exception checking OSINT Search: {e}")
        return None