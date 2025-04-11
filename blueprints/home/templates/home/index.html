# blueprints/ai_analysis/routes.py
from flask import render_template, request, jsonify, current_app, session, flash, redirect, url_for
from flask_login import current_user, login_required
from blueprints.ai_analysis import ai_analysis_bp
from blueprints.ai_analysis.utils import generate_osint_analysis, generate_security_recommendations
from datetime import datetime
import json
from models import db, Scan

@ai_analysis_bp.route('/')
def index():
    return render_template('ai_analysis/index.html', now=datetime.now())

@ai_analysis_bp.route('/analyze', methods=['POST'])
def analyze():
    analysis_type = request.form.get('analysis_type')
    target = request.form.get('target')
    
    if not analysis_type or not target:
        return jsonify({'error': 'Analysis type and target are required'}), 400
    
    # Create results dictionary
    results = {
        'target': target,
        'analysis_type': analysis_type,
        'scan_date': datetime.now(),
        'insights': [],
        'recommendations': [],
        'risk_score': 0
    }
    
    # Generate analysis based on type
    if analysis_type == 'username':
        # Simulate results from previous username search
        mock_accounts = [
            {'site_name': 'Twitter', 'category': 'Social Media'},
            {'site_name': 'LinkedIn', 'category': 'Professional'},
            {'site_name': 'GitHub', 'category': 'Professional'},
            {'site_name': 'Reddit', 'category': 'Forums'}
        ]
        
        insights = generate_osint_analysis(target, 'username', mock_accounts)
        recommendations = generate_security_recommendations('username', insights)
        
        results['insights'] = insights
        results['recommendations'] = recommendations
        results['risk_score'] = 45  # Example score
        
    elif analysis_type == 'email':
        # Simulate results from previous data breach search
        mock_breaches = [
            {'name': 'LinkedIn', 'date': '2012-05-05', 'data_types': ['Email', 'Password']},
            {'name': 'Adobe', 'date': '2013-10-04', 'data_types': ['Email', 'Password', 'Address']}
        ]
        
        insights = generate_osint_analysis(target, 'email', mock_breaches)
        recommendations = generate_security_recommendations('email', insights)
        
        results['insights'] = insights
        results['recommendations'] = recommendations
        results['risk_score'] = 65  # Example score
        
    elif analysis_type == 'domain':
        # Simulate domain analysis results
        mock_domain_data = {
            'registrar': 'GoDaddy',
            'creation_date': '2010-01-15',
            'expiration_date': '2025-01-15',
            'nameservers': ['ns1.example.com', 'ns2.example.com']
        }
        
        insights = generate_osint_analysis(target, 'domain', mock_domain_data)
        recommendations = generate_security_recommendations('domain', insights)
        
        results['insights'] = insights
        results['recommendations'] = recommendations
        results['risk_score'] = 30  # Example score
        
    elif analysis_type == 'combined':
        # Combine multiple data sources for a comprehensive analysis
        mock_combined_data = {
            'username_findings': [{'site_name': 'Twitter'}, {'site_name': 'LinkedIn'}],
            'email_findings': [{'name': 'Adobe', 'data_types': ['Email', 'Password']}],
            'domain_findings': {'registrar': 'GoDaddy', 'creation_date': '2015-05-10'}
        }
        
        insights = generate_osint_analysis(target, 'combined', mock_combined_data)
        recommendations = generate_security_recommendations('combined', insights)
        
        results['insights'] = insights
        results['recommendations'] = recommendations
        results['risk_score'] = 75  # Example score
    
    # Save results to database if user is logged in
    if current_user.is_authenticated:
        # Convert the results to JSON for storage
        results_json = json.dumps(results, default=str)
        
        # Create a new scan record
        new_scan = Scan(
            user_id=current_user.id,
            scan_type='ai_analysis',
            target=target,
            scan_date=datetime.now(),
            status='completed',
            findings=len(results['insights']),
            results_json=results_json,
            risk_score=results['risk_score']
        )
        
        db.session.add(new_scan)
        db.session.commit()
    
    return render_template('ai_analysis/results.html', results=results, now=datetime.now())

@ai_analysis_bp.route('/show_saved_results/<int:scan_id>')
@login_required
def show_saved_results(scan_id):
    # Get the saved scan from database
    scan = Scan.query.filter_by(id=scan_id, user_id=current_user.id).first_or_404()
    
    if scan.scan_type != 'ai_analysis':
        flash('Invalid scan type', 'error')
        return redirect(url_for('home.my_scans'))
    
    try:
        # Deserialize the JSON results
        results = json.loads(scan.results_json)
        
        # Convert date strings back to datetime objects if needed
        if isinstance(results.get('scan_date'), str):
            results['scan_date'] = datetime.fromisoformat(results['scan_date'].replace('Z', '+00:00'))
        
        return render_template('ai_analysis/results.html', results=results, now=datetime.now(), scan_id=scan.id)
    except Exception as e:
        print(f"Error displaying saved results: {e}")
        flash('Error loading saved scan results', 'error')
        return redirect(url_for('home.my_scans'))