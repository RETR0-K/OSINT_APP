# blueprints/data_breach/routes.py
from flask import render_template, request, current_app, jsonify
from blueprints.data_breach import data_breach_bp
from blueprints.data_breach.utils import check_haveibeenpwned, check_breachdirectory, check_dehashed
from datetime import datetime

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
        'sources': []
    }
    
    # Check HaveIBeenPwned
    hibp_result = check_haveibeenpwned(email, current_app.config['HAVEIBEENPWNED_API_KEY'])
    if hibp_result:
        results['sources'].append({
            'name': 'HaveIBeenPwned',
            'breaches': hibp_result
        })
    
    # Check BreachDirectory
    breach_dir_result = check_breachdirectory(email, current_app.config['BREACHDIRECTORY_API_KEY'])
    if breach_dir_result:
        results['sources'].append({
            'name': 'BreachDirectory',
            'breaches': breach_dir_result
        })
    
    # Check DeHashed
    dehashed_result = check_dehashed(email, current_app.config['DEHASHED_API_KEY'])
    if dehashed_result:
        results['sources'].append({
            'name': 'DeHashed',
            'breaches': dehashed_result
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
    
    return render_template('data_breach/results.html', results=results, now=datetime.now())