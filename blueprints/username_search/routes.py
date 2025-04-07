# blueprints/username_search/routes.py
from flask import render_template, request, jsonify, current_app
from blueprints.username_search import username_search_bp
from blueprints.username_search.utils import search_sherlock, search_whatsmyname
from datetime import datetime
import json
import os

@username_search_bp.route('/')
def index():
    return render_template('username_search/index.html', now=datetime.now())

@username_search_bp.route('/search', methods=['POST'])
def search():
    username = request.form.get('username', '')
    if not username:
        return jsonify({'error': 'Username is required'}), 400
    
    # Create results structure
    results = {
        'username': username,
        'scan_date': datetime.now(),
        'sherlock': None,
        'whatsmyname': None,
        'total_found': 0,
        'categories': {}
    }
    
    # Run Sherlock search
    sherlock_results = search_sherlock(username)
    if sherlock_results:
        results['sherlock'] = sherlock_results
        
    # Run WhatsMyName search
    whatsmyname_results = search_whatsmyname(username)
    if whatsmyname_results:
        results['whatsmyname'] = whatsmyname_results
    
    # Combine and categorize results
    combined_results = []
    categories = {}
    
    # Process Sherlock results
    if results['sherlock']:
        for site in results['sherlock']:
            combined_results.append({
                'site_name': site['site_name'],
                'url': site['url'],
                'category': site.get('category', 'Uncategorized'),
                'source': 'Sherlock'
            })
    
    # Process WhatsMyName results
    if results['whatsmyname']:
        for site in results['whatsmyname']:
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
    
    results['combined_results'] = combined_results
    results['categories'] = categories
    results['total_found'] = len(combined_results)
    
    # Calculate risk score based on number of accounts found
    if results['total_found'] == 0:
        risk_score = 0
    elif results['total_found'] <= 5:
        risk_score = 10
    elif results['total_found'] <= 15:
        risk_score = 25
    elif results['total_found'] <= 30:
        risk_score = 50
    elif results['total_found'] <= 50:
        risk_score = 75
    else:
        risk_score = 100
    
    results['risk_score'] = risk_score
    
    return render_template('username_search/results.html', results=results, now=datetime.now())