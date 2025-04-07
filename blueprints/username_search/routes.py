# blueprints/username_search/routes.py
from flask import render_template, request, jsonify, current_app, session, redirect, url_for
from blueprints.username_search import username_search_bp
from blueprints.username_search.utils import start_search, get_search_progress, get_search_results
from datetime import datetime
import json
import os
import uuid

# In-memory storage for search progress (in a real app, you'd use Redis or another persistent store)
active_searches = {}

@username_search_bp.route('/')
def index():
    return render_template('username_search/index.html', now=datetime.now())

@username_search_bp.route('/search-start', methods=['POST'])
def search_start():
    """Start a new username search and return a search ID"""
    username = request.form.get('username', '')
    if not username:
        return jsonify({'error': 'Username is required'}), 400
    
    # Generate a unique search ID
    search_id = str(uuid.uuid4())
    
    # Initialize search progress
    active_searches[search_id] = {
        'username': username,
        'start_time': datetime.now(),
        'is_complete': False,
        'sherlock': {
            'status': 'starting',
            'percent': 0,
            'found': 0,
            'sites_checked': 0,
            'total_sites': 0
        },
        'whatsmyname': {
            'status': 'starting',
            'percent': 0,
            'found': 0,
            'sites_checked': 0,
            'total_sites': 0
        },
        'results': None
    }
    
    # Start the search in the background
    start_search(username, search_id, active_searches)
    
    return jsonify({
        'search_id': search_id,
        'message': 'Search started'
    })

@username_search_bp.route('/search-progress', methods=['POST'])
def search_progress():
    """Get the current progress of a search"""
    username = request.form.get('username', '')
    search_id = request.form.get('search_id', '')
    
    if not search_id or search_id not in active_searches:
        # If no search ID provided or not found, try to find by username
        for sid, search_data in active_searches.items():
            if search_data['username'] == username:
                search_id = sid
                break
        
        if not search_id:
            return jsonify({
                'error': 'Search not found',
                'is_complete': False
            }), 404
    
    # Get the current progress
    search_data = active_searches[search_id]
    
    # Check if the search is complete
    if search_data['is_complete']:
        return jsonify({
            'is_complete': True,
            'search_id': search_id,
            'status': 'Search complete'
        })
    
    # Get real-time progress
    progress = get_search_progress(search_id, active_searches)
    
    return jsonify({
        'is_complete': progress['is_complete'],
        'sherlock': progress['sherlock'],
        'whatsmyname': progress['whatsmyname'],
        'status': progress['status'],
        'search_id': search_id
    })

@username_search_bp.route('/results/<search_id>')
def results(search_id):
    """Show the results of a completed search"""
    if search_id not in active_searches:
        return redirect(url_for('username_search.index'))
    
    search_data = active_searches[search_id]
    if not search_data['is_complete']:
        # If the search is not complete, redirect to a waiting page or show progress
        return render_template('username_search/searching.html', 
                             search_id=search_id, 
                             username=search_data['username'],
                             now=datetime.now())
    
    # Get the results
    results = get_search_results(search_id, active_searches)
    
    return render_template('username_search/results.html', results=results, now=datetime.now())

@username_search_bp.route('/search', methods=['POST'])
def search():
    """Legacy route for compatibility - starts a search and immediately shows searching page"""
    username = request.form.get('username', '')
    if not username:
        return jsonify({'error': 'Username is required'}), 400
    
    # Generate a unique search ID
    search_id = str(uuid.uuid4())
    
    # Initialize search progress
    active_searches[search_id] = {
        'username': username,
        'start_time': datetime.now(),
        'is_complete': False,
        'sherlock': {
            'status': 'starting',
            'percent': 0,
            'found': 0,
            'sites_checked': 0,
            'total_sites': 0
        },
        'whatsmyname': {
            'status': 'starting',
            'percent': 0,
            'found': 0,
            'sites_checked': 0,
            'total_sites': 0
        },
        'results': None
    }
    
    # Start the search in the background
    start_search(username, search_id, active_searches)
    
    # Redirect to the searching page
    return render_template('username_search/searching.html', 
                         search_id=search_id, 
                         username=username,
                         now=datetime.now())