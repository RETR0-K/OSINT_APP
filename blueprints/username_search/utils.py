# blueprints/username_search/utils.py
import subprocess
import json
import os
import requests
from flask import current_app
import tempfile
import time
import random

def search_sherlock(username):
    """
    Search for username across various platforms using Sherlock
    For a real implementation, you would install Sherlock and call it properly.
    This is a mock implementation for development.
    """
    # In a real implementation, you would run Sherlock as a subprocess
    # Command would be something like:
    # result = subprocess.run(['sherlock', username, '--output', output_file, '--json'], 
    #                        capture_output=True, text=True)
    
    # For development, return mock data
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
    
    # Combine all categories
    mock_results = social_media + professional + forums + gaming
    
    # Randomly remove some results to simulate not finding all accounts
    random.shuffle(mock_results)
    return mock_results[:random.randint(5, len(mock_results))]

def search_whatsmyname(username):
    """
    Search for username across various platforms using WhatsMyName
    For a real implementation, you would use the WhatsMyName data or API.
    This is a mock implementation for development.
    """
    # In a real implementation, you would either:
    # 1. Use the WhatsMyName API if available
    # 2. Use the WhatsMyName JSON data file and check each site
    
    # For development, return mock data
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
    
    # Combine all categories
    mock_results = media_sharing + dating + shopping + tech
    
    # Randomly remove some results to simulate not finding all accounts
    random.shuffle(mock_results)
    return mock_results[:random.randint(3, len(mock_results))]