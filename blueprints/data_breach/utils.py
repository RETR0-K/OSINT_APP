# blueprints/data_breach/utils.py
import requests
import json
import time
from datetime import datetime
import os

def check_xposedornot(email):
    """
    Check if an email has been compromised using the XposedOrNot API.
    
    This function implements two API calls from XposedOrNot:
    1. Simple check to see if email is in any breaches
    2. Detailed breach analytics if a breach is found
    
    Based on XposedOrNot API documentation: https://xposedornot.com/api_doc
    """
    # For demo/development, return mock data if running in development mode with mock data enabled
    if os.environ.get('FLASK_ENV') == 'development' and os.environ.get('USE_MOCK_DATA') == 'True':
        # Mock data based on XposedOrNot API response format
        return {
            'found': True,
            'total_breaches': 3,
            'breaches': [
                {
                    'source': 'SweClockers',
                    'breach_date': '2015-01-01',
                    'description': 'SweClockers experienced a data breach in early 2015, where 255k accounts were exposed. Usernames, email addresses, and salted hashes of passwords were disclosed.',
                    'exposed_data': 'Usernames, Email addresses, Passwords',
                    'risk_level': 'Low',
                    'breach_size': '254,967 records'
                },
                {
                    'source': 'LinkedIn',
                    'breach_date': '2012-05-05',
                    'description': 'LinkedIn suffered a breach exposing 164 million email addresses and passwords. The passwords were stored as SHA1 hashes without salt.',
                    'exposed_data': 'Email addresses, Passwords, Professional information',
                    'risk_level': 'High',
                    'breach_size': '164,611,595 records'
                },
                {
                    'source': 'Adobe',
                    'breach_date': '2013-10-04',
                    'description': 'Adobe experienced a security breach exposing account information of 153 million users. The breach included email addresses, encrypted passwords, and password hints.',
                    'exposed_data': 'Email addresses, Passwords, Password hints, Countries',
                    'risk_level': 'High',
                    'breach_size': '152,445,165 records'
                }
            ]
        }
    
    # Step 1: Simple breach check
    # Use the "Check for Email Address Data Breaches" API endpoint
    email_check_url = f"https://api.xposedornot.com/v1/check-email/{email}"
    
    try:
        # Make the first API call
        response = requests.get(email_check_url)
        
        # Check for rate limiting
        if response.status_code == 429:
            print("Rate limited by XposedOrNot API. Waiting 2 seconds...")
            time.sleep(2)
            return check_xposedornot(email)
        
        # If response is not successful, return not found
        if response.status_code != 200:
            print(f"Error checking XposedOrNot (status code {response.status_code}): {response.text}")
            return {'found': False, 'total_breaches': 0, 'breaches': []}
        
        # Parse the response
        breach_check_data = response.json()
        
        # Check if email was found in any breaches
        if "Error" in breach_check_data and breach_check_data["Error"] == "Not found":
            return {'found': False, 'total_breaches': 0, 'breaches': []}
        
        # If we get here, breaches were found. Get the list of breach names
        breach_names = []
        if "breaches" in breach_check_data and len(breach_check_data["breaches"]) > 0:
            breach_names = breach_check_data["breaches"][0]
        
        # Step 2: Get detailed breach analytics
        # Use the "Data Breach Analytics for Email Addresses" API endpoint
        analytics_url = f"https://api.xposedornot.com/v1/breach-analytics?email={email}"
        
        analytics_response = requests.get(analytics_url)
        
        # Check for rate limiting
        if analytics_response.status_code == 429:
            print("Rate limited by XposedOrNot API. Waiting 2 seconds...")
            time.sleep(2)
            # Try just the analytics part again
            analytics_response = requests.get(analytics_url)
        
        # If analytics response is successful, parse the detailed breach data
        if analytics_response.status_code == 200:
            analytics_data = analytics_response.json()
            
            # Format the detailed breach information
            breaches = []
            
            # Check if there are exposed breaches in the analytics data
            if "ExposedBreaches" in analytics_data and analytics_data["ExposedBreaches"]:
                exposed_breaches = analytics_data["ExposedBreaches"].get("breaches_details", [])
                
                for breach in exposed_breaches:
                    breaches.append({
                        'source': breach.get('breach', 'Unknown'),
                        'breach_date': breach.get('xposed_date', 'Unknown'),
                        'description': breach.get('details', 'No details available'),
                        'exposed_data': breach.get('xposed_data', 'Unknown').replace(';', ', '),
                        'risk_level': _get_risk_level(breach.get('password_risk', 'unknown')),
                        'breach_size': f"{breach.get('xposed_records', 0):,} records"
                    })
            
            # Calculate risk score from metrics if available
            risk_score = 0
            if "BreachMetrics" in analytics_data:
                metrics = analytics_data["BreachMetrics"]
                if "risk" in metrics and len(metrics["risk"]) > 0:
                    risk_data = metrics["risk"][0]
                    risk_score = risk_data.get("risk_score", 0)
            
            return {
                'found': True,
                'total_breaches': len(breaches),
                'breaches': breaches,
                'risk_score': risk_score
            }
        else:
            # Fallback to basic breach information if analytics fails
            breaches = []
            for breach_name in breach_names:
                breaches.append({
                    'source': breach_name,
                    'breach_date': 'Unknown',
                    'description': 'Details not available',
                    'exposed_data': 'Unknown',
                    'risk_level': 'Unknown',
                    'breach_size': 'Unknown'
                })
            
            return {
                'found': True,
                'total_breaches': len(breach_names),
                'breaches': breaches
            }
        
    except Exception as e:
        print(f"Exception checking XposedOrNot: {e}")
        return None

def _get_risk_level(password_risk):
    """Convert password_risk from XposedOrNot to risk level"""
    risk_map = {
        'plaintext': 'Critical',
        'easytocrack': 'High',
        'hardtocrack': 'Low',
        'unknown': 'Unknown'
    }
    return risk_map.get(password_risk.lower(), 'Unknown')