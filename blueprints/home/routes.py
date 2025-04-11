# blueprints/home/routes.py
from flask import render_template, current_app, redirect, url_for
from flask_login import current_user, login_required
from datetime import datetime
from blueprints.home import home_bp
from models import db, Scan
from blueprints.home.utils import export_scan_to_json, export_scan_to_csv, export_scans_to_csv


@home_bp.route('/')
def index():
    if current_user.is_authenticated:
        # Get user's recent scans
        recent_scans = Scan.query.filter_by(user_id=current_user.id).order_by(Scan.scan_date.desc()).limit(5).all()
        
        # Calculate stats based on user's scan history
        total_scans = Scan.query.filter_by(user_id=current_user.id).count()
        
        # Count breaches found (for data breach scans)
        breach_scans = Scan.query.filter_by(user_id=current_user.id, scan_type='email').all()
        breaches_found = sum(scan.findings for scan in breach_scans)
        
        # Count accounts discovered (for username scans)
        username_scans = Scan.query.filter_by(user_id=current_user.id, scan_type='username').all()
        accounts_discovered = sum(scan.findings for scan in username_scans)
        
        # Calculate average risk score
        all_scans = Scan.query.filter_by(user_id=current_user.id).all()
        if all_scans:
            avg_risk_score = sum(scan.risk_score for scan in all_scans) // len(all_scans)
        else:
            avg_risk_score = 0
        
        stats = {
            'total_scans': total_scans,
            'breaches_found': breaches_found,
            'accounts_discovered': accounts_discovered,
            'risk_score': avg_risk_score
        }
    else:
        # Example data for dashboard for non-authenticated users
        recent_scans = [
            {
                'id': 1,
                'target': 'johndoe',
                'scan_type': 'username',
                'scan_date': datetime(2025, 4, 5, 14, 30),
                'status': 'completed',
                'findings': 12
            },
            {
                'id': 2,
                'target': 'jane.smith@example.com',
                'scan_type': 'email',
                'scan_date': datetime(2025, 4, 5, 10, 15),
                'status': 'completed',
                'findings': 3
            },
            {
                'id': 3,
                'target': 'mikebrown',
                'scan_type': 'username',
                'scan_date': datetime(2025, 4, 4, 16, 45),
                'status': 'completed',
                'findings': 8
            }
        ]
        
        stats = {
            'total_scans': 24,
            'breaches_found': 47,
            'accounts_discovered': 132,
            'risk_score': 68
        }
    
    return render_template('home/index.html', 
                           recent_scans=recent_scans, 
                           stats=stats,
                           now=datetime.now())

@home_bp.route('/my-scans')
@login_required
def my_scans():
    # Get all user's scans
    scans = Scan.query.filter_by(user_id=current_user.id).order_by(Scan.scan_date.desc()).all()
    
    return render_template('home/my_scans.html', scans=scans, now=datetime.now())

@home_bp.route('/scan/<int:scan_id>')
@login_required
def view_scan(scan_id):
    # Get the specific scan
    scan = Scan.query.filter_by(id=scan_id, user_id=current_user.id).first_or_404()
    
    # Redirect to the appropriate results page based on scan type
    if scan.scan_type == 'username':
        return redirect(url_for('username_search.show_saved_results', scan_id=scan.id))
    elif scan.scan_type == 'email':
        return redirect(url_for('data_breach.show_saved_results', scan_id=scan.id))
    elif scan.scan_type == 'ai_analysis':
        return redirect(url_for('ai_analysis.show_saved_results', scan_id=scan.id))
    else:
        # Default fallback
        return redirect(url_for('home.my_scans'))

@home_bp.route('/scan/<int:scan_id>/delete')
@login_required
def delete_scan(scan_id):
    scan = Scan.query.filter_by(id=scan_id, user_id=current_user.id).first_or_404()
    
    db.session.delete(scan)
    db.session.commit()
    
    return redirect(url_for('home.my_scans'))

@home_bp.route('/scan/<int:scan_id>/export/json')
@login_required
def export_scan_json(scan_id):
    """Export a scan in JSON format"""
    scan = Scan.query.filter_by(id=scan_id, user_id=current_user.id).first_or_404()
    return export_scan_to_json(scan)

@home_bp.route('/scan/<int:scan_id>/export/csv')
@login_required
def export_scan_csv(scan_id):
    """Export a scan in CSV format"""
    scan = Scan.query.filter_by(id=scan_id, user_id=current_user.id).first_or_404()
    return export_scan_to_csv(scan)

@home_bp.route('/export/all/csv')
@login_required
def export_all_scans_csv():
    """Export all user scans in CSV format"""
    scans = Scan.query.filter_by(user_id=current_user.id).all()
    return export_scans_to_csv(scans)
