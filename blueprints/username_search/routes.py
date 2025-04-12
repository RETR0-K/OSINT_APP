# blueprints/username_search/routes.py
from flask import render_template, request, jsonify, redirect, url_for, flash, session
from flask_login import current_user, login_required
from blueprints.username_search import username_search_bp
from blueprints.username_search.utils import search_username, get_search_progress
from datetime import datetime
import json
import os
import tempfile
import traceback
from models import db, Scan

@username_search_bp.route('/')
def index():
    return render_template('username_search/index.html', now=datetime.now())

@username_search_bp.route('/search', methods=['POST'])
def search():
    """
    Start the username search process and show the searching page
    """
    username = request.form.get('username', '')
    if not username:
        return redirect(url_for('username_search.index'))
    
    # Store username in session for the progress page
    session['search_username'] = username
    
    # Redirect to the searching page
    return render_template('username_search/searching.html', username=username)

@username_search_bp.route('/process_search', methods=['POST'])
def process_search():
    """
    Process the username search in the background and return the results
    """
    try:
        username = request.form.get('username', '')
        if not username:
            return jsonify({'success': False, 'error': 'Username is required'})
        
        print(f"Starting search for username: {username}")
        
        # Start the search
        search_result = search_username(username)
        
        print(f"Search completed. Processing results...")
        
        # Combine results for the final output
        combined_results = []
        
        # Process Sherlock results
        sherlock_results = search_result.get('sherlock', [])
        for site in sherlock_results:
            combined_results.append(site)
        
        # Process WhatsMyName results
        whatsmyname_results = search_result.get('whatsmyname', [])
        for site in whatsmyname_results:
            # Check if this site is already in results from Sherlock
            if not any(r['site_name'] == site['site_name'] for r in combined_results):
                combined_results.append(site)
        
        # Count categories
        categories = {}
        for result in combined_results:
            category = result['category']
            if category not in categories:
                categories[category] = 0
            categories[category] += 1
        
        # Calculate risk score based on number of accounts found
        total_found = len(combined_results)
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
        
        # Create results object
        scan_results = {
            'username': username,
            'scan_date': datetime.now(),
            'sherlock': sherlock_results,
            'whatsmyname': whatsmyname_results,
            'combined_results': combined_results,
            'categories': categories,
            'total_found': total_found,
            'risk_score': risk_score
        }
        
        # Save results to database if user is logged in
        if current_user.is_authenticated:
            try:
                # Convert the results to JSON for storage
                results_json = json.dumps(scan_results, default=str)
                
                # Create a new scan record
                new_scan = Scan(
                    user_id=current_user.id,
                    scan_type='username',
                    target=username,
                    scan_date=datetime.now(),
                    status='completed',
                    findings=total_found,
                    results_json=results_json,
                    risk_score=risk_score
                )
                
                db.session.add(new_scan)
                db.session.commit()
            except Exception as e:
                print(f"Error saving scan to database: {e}")
                # Continue without saving to database
        
        print(f"Returning final results with {total_found} accounts found")
        
        # Return success response with the results
        return jsonify({'success': True, 'results': scan_results})
    
    except Exception as e:
        print(f"Error in username search: {e}")
        print(traceback.format_exc())
        return jsonify({'success': False, 'error': str(e)})

@username_search_bp.route('/check_progress')
def check_progress():
    """
    Check the current progress of an ongoing search
    """
    progress_file = request.args.get('progress_file', '')
    username = session.get('search_username', '')
    
    if not progress_file:
        # Try to find the most recent progress file for this username
        temp_dir = tempfile.gettempdir()
        potential_files = [f for f in os.listdir(temp_dir) if f.startswith(f"search_progress_{username}_") and f.endswith(".json")]
        if potential_files:
            # Sort by creation time, newest first
            potential_files.sort(key=lambda f: os.path.getctime(os.path.join(temp_dir, f)), reverse=True)
            progress_file = os.path.join(temp_dir, potential_files[0])
    
    if not progress_file or not os.path.exists(progress_file):
        # If progress file does not exist, return a default progress message
        return jsonify({
            'sherlock': {'status': 'starting', 'message': 'Starting search...', 'found': 0, 'total_checked': 0},
            'whatsmyname': {'status': 'starting', 'message': 'Starting search...', 'found': 0, 'total_checked': 0}
        })
    
    # Read the progress file
    progress = get_search_progress(progress_file)
    if progress:
        return jsonify(progress)
    else:
        return jsonify({
            'sherlock': {'status': 'error', 'message': 'Error reading progress', 'found': 0, 'total_checked': 0},
            'whatsmyname': {'status': 'error', 'message': 'Error reading progress', 'found': 0, 'total_checked': 0}
        })

@username_search_bp.route('/show_results', methods=['POST'])
def show_results():
    """
    Display the search results
    """
    results_json = request.form.get('results', '{}')
    try:
        results = json.loads(results_json)
        return render_template('username_search/results.html', results=results, now=datetime.now())
    except Exception as e:
        print(f"Error displaying results: {e}")
        flash("Error displaying search results", "error")
        return redirect(url_for('username_search.index'))

@username_search_bp.route('/show_saved_results/<int:scan_id>')
@login_required
def show_saved_results(scan_id):
    # Get the saved scan from database
    scan = Scan.query.filter_by(id=scan_id, user_id=current_user.id).first_or_404()
    
    if scan.scan_type != 'username':
        flash('Invalid scan type', 'error')
        return redirect(url_for('home.my_scans'))
    
    try:
        # Deserialize the JSON results
        results = json.loads(scan.results_json)
        
        # Convert date strings back to datetime objects if needed
        if isinstance(results.get('scan_date'), str):
            results['scan_date'] = datetime.fromisoformat(results['scan_date'].replace('Z', '+00:00'))
        
        return render_template('username_search/results.html', results=results, now=datetime.now(), scan_id=scan.id)
    except Exception as e:
        print(f"Error displaying saved results: {e}")
        flash('Error loading saved scan results', 'error')
        return redirect(url_for('home.my_scans'))