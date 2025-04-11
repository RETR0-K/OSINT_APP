# blueprints/data_breach/routes.py
from flask import render_template, request, current_app, jsonify, flash, redirect, url_for, Blueprint
from flask_login import current_user, login_required
from blueprints.data_breach import data_breach_bp
from blueprints.data_breach.utils import check_breach_directory, check_breach_search, check_osint_search
from datetime import datetime
import json
from models import db, Scan

@data_breach_bp.route('/')
def index():
    return render_template('data_breach/index.html', now=datetime.now())

@data_breach_bp.route('/check', methods=['POST'])
def check_email():
    email = request.form.get('email', '')
    if not email:
        return jsonify({'error': 'Email is required'}), 400
    
    # Collect results from different APIs
    results = {
        'email': email,
        'scan_date': datetime.now(),
        'sources': [],
        'total_breaches': 0
    }
    
    # Get API key
    rapidapi_key = current_app.config.get('RAPIDAPI_KEY')
    
    # Check BreachDirectory API
    breach_dir_result = check_breach_directory(email, rapidapi_key)
    if breach_dir_result:
        results['sources'].append({
            'name': 'BreachDirectory',
            'breaches': breach_dir_result
        })
    
    # Check BreachSearch API
    breach_search_result = check_breach_search(email, rapidapi_key)
    if breach_search_result:
        results['sources'].append({
            'name': 'BreachSearch',
            'breaches': breach_search_result
        })
    
    # Check OSINT Search API
    osint_search_result = check_osint_search(email, rapidapi_key)
    if osint_search_result:
        results['sources'].append({
            'name': 'OSINT Search',
            'breaches': osint_search_result.get('breaches', [])
        })
    
    # Count total breaches
    total_breaches = sum(len(source['breaches']) for source in results['sources'])
    results['total_breaches'] = total_breaches
    
    # Calculate risk score (simplified version)
    if total_breaches == 0:
        risk_score = 0
    elif total_breaches <= 2:
        risk_score = 25
    elif total_breaches <= 5:
        risk_score = 50
    elif total_breaches <= 10:
        risk_score = 75
    else:
        risk_score = 100
    
    results['risk_score'] = risk_score
    
    # Save results to database if user is logged in
    if current_user.is_authenticated:
        # Convert the results to JSON for storage
        results_json = json.dumps(results, default=str)
        
        # Create a new scan record
        new_scan = Scan(
            user_id=current_user.id,
            scan_type='email',
            target=email,
            scan_date=datetime.now(),
            status='completed',
            findings=total_breaches,
            results_json=results_json,
            risk_score=risk_score
        )
        
        db.session.add(new_scan)
        db.session.commit()
    
    return render_template('data_breach/results.html', results=results, now=datetime.now())

@data_breach_bp.route('/show_saved_results/<int:scan_id>')
@login_required
def show_saved_results(scan_id):
    # Get the saved scan from database
    scan = Scan.query.filter_by(id=scan_id, user_id=current_user.id).first_or_404()
    
    if scan.scan_type != 'email':
        flash('Invalid scan type', 'error')
        return redirect(url_for('home.my_scans'))
    
    try:
        # Deserialize the JSON results
        results = json.loads(scan.results_json)
        
        # Convert date strings back to datetime objects if needed
        if isinstance(results.get('scan_date'), str):
            results['scan_date'] = datetime.fromisoformat(results['scan_date'].replace('Z', '+00:00'))
        
        return render_template('data_breach/results.html', results=results, now=datetime.now(), scan_id=scan.id)
    except Exception as e:
        print(f"Error displaying saved results: {e}")
        flash('Error loading saved scan results', 'error')
        return redirect(url_for('home.my_scans'))