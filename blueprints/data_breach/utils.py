# blueprints/data_breach/utils.py
import requests
import json
import hashlib

def check_haveibeenpwned(email, api_key):
    """
    Check if an email has been compromised using the HaveIBeenPwned API
    """
    if not api_key:
        # Return example data for development without API key
        return [
            {
                'Name': 'LinkedIn',
                'BreachDate': '2012-05-05',
                'Description': 'In May 2016, LinkedIn had 164 million email addresses and passwords exposed.',
                'DataClasses': ['Email addresses', 'Passwords']
            }
        ]
    
    url = f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}"
    headers = {
        'hibp-api-key': api_key,
        'User-Agent': 'OSINT-Tracker'
    }
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            return []  # No breaches found
        else:
            print(f"Error checking HaveIBeenPwned: {response.status_code}")
            return None
    except Exception as e:
        print(f"Exception checking HaveIBeenPwned: {e}")
        return None

def check_breachdirectory(email, api_key):
    """
    Check if an email has been compromised using the BreachDirectory API
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
            return data.get('result', [])
        else:
            print(f"Error checking BreachDirectory: {response.status_code}")
            return None
    except Exception as e:
        print(f"Exception checking BreachDirectory: {e}")
        return None

def check_dehashed(email, api_key):
    """
    Check if an email has been compromised using the DeHashed API
    """
    if not api_key:
        # Return example data for development without API key
        return [
            {
                'name': 'Canva',
                'breach_date': '2019-05-24',
                'password': '********',
                'hashed_password': 'bcrypt$********',
                'database_name': 'Canva'
            }
        ]
    
    # DeHashed requires username:api_key authentication
    # This is just a placeholder implementation
    url = "https://api.dehashed.com/search"
    headers = {
        'Accept': 'application/json'
    }
    params = {
        'query': f'email:{email}'
    }
    
    try:
        response = requests.get(url, headers=headers, params=params, auth=('username', api_key))
        if response.status_code == 200:
            data = response.json()
            return data.get('entries', [])
        else:
            print(f"Error checking DeHashed: {response.status_code}")
            return None
    except Exception as e:
        print(f"Exception checking DeHashed: {e}")
        return None