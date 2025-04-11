# blueprints/username_search/routes.py
from flask import render_template, request, jsonify, current_app, redirect, url_for, flash
from flask_login import current_user, login_required
from blueprints.username_search import username_search_bp
from blueprints.username_search.utils import search_username
from datetime import datetime
import json
from models import db, Scan

@username_search_bp.route('/')
def index():
    return render_template('username_search/index.html', now=datetime.now())

@username_search_bp.route('/search', methods=['POST'])
def search():
    """
    Process the username search and show results directly
    """
    username = request.form.get('username', '')
    if not username:
        return redirect(url_for('username_search.index'))
    
    try:
        # Run the search
        search_results = search_username(username)
        
        # Process and combine results
        combined_results = []
        categories = {}
        
        # Process Sherlock results
        sherlock_results = search_results.get('sherlock', [])
        for site in sherlock_results:
            combined_results.append({
                'site_name': site['site_name'],
                'url': site['url'],
                'category': site.get('category', 'Uncategorized'),
                'source': 'Sherlock'
            })
        
        # Process WhatsMyName results
        whatsmyname_results = search_results.get('whatsmyname', [])
        for site in whatsmyname_results:
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
        
        # Display results
        return render_template('username_search/results.html', results=scan_results, now=datetime.now())
        
    except Exception as e:
        print(f"Error in search: {e}")
        # On error, redirect back to search form
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