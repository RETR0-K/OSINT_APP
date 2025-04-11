# blueprints/data_breach/routes.py
from flask import render_template, request, flash, redirect, url_for
from flask_login import current_user, login_required
from blueprints.data_breach import data_breach_bp
from blueprints.data_breach.utils import check_xposedornot
from datetime import datetime
import json
import traceback
from models import db, Scan

@data_breach_bp.route('/')
def index():
    return render_template('data_breach/index.html', now=datetime.now())

@data_breach_bp.route('/check', methods=['POST'])
def check_email():
    try:
        email = request.form.get('email', '')
        if not email:
            flash('Email address is required', 'error')
            return redirect(url_for('data_breach.index'))
        
        # Collect results from XposedOrNot API
        results = {
            'email': email,
            'scan_date': datetime.now(),
            'sources': [],
            'total_breaches': 0
        }
        
        # Check XposedOrNot API (no API key required)
        xposedornot_result = check_xposedornot(email)
        if xposedornot_result and xposedornot_result.get('found', False):
            formatted_breaches = []
            for breach in xposedornot_result.get('breaches', []):
                formatted_breaches.append({
                    'source': breach.get('source', 'Unknown'),
                    'breach_date': breach.get('breach_date', 'Unknown'),
                    'description': breach.get('description', 'No details available'),
                    'exposed_data': breach.get('exposed_data', 'Unknown'),
                    'risk_level': breach.get('risk_level', 'Unknown'),
                    'breach_size': breach.get('breach_size', 'Unknown')
                })
            
            if formatted_breaches:
                results['sources'].append({
                    'name': 'XposedOrNot',
                    'breaches': formatted_breaches
                })
        
        # Count total breaches
        total_breaches = sum(len(source['breaches']) for source in results['sources'])
        results['total_breaches'] = total_breaches
        
        # Calculate risk score
        # Use XposedOrNot's risk score if available
        if xposedornot_result and 'risk_score' in xposedornot_result:
            risk_score = xposedornot_result['risk_score']
        else:
            # Fallback calculation based on number of breaches
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
            try:
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
            except Exception as e:
                print(f"Error saving scan to database: {e}")
                # Continue without saving to database
        
        return render_template('data_breach/results.html', results=results, now=datetime.now())
    
    except Exception as e:
        print(f"Error checking data breaches: {e}")
        print(traceback.format_exc())
        flash("An error occurred while checking data breaches. Please try again later.", "error")
        return redirect(url_for('data_breach.index'))

@data_breach_bp.route('/show_saved_results/<int:scan_id>')
@login_required
def show_saved_results(scan_id):
    try:
        # Get the saved scan from database
        scan = Scan.query.filter_by(id=scan_id, user_id=current_user.id).first_or_404()
        
        if scan.scan_type != 'email':
            flash('Invalid scan type', 'error')
            return redirect(url_for('home.my_scans'))
        
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