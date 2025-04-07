# blueprints/ai_analysis/routes.py
from flask import render_template, request, jsonify, current_app, session
from blueprints.ai_analysis import ai_analysis_bp
from blueprints.ai_analysis.utils import generate_osint_analysis, generate_security_recommendations
from datetime import datetime
import json

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
    
    return render_template('ai_analysis/results.html', results=results, now=datetime.now())