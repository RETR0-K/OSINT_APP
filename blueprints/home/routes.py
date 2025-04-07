# blueprints/home/routes.py
from flask import render_template, current_app
from datetime import datetime
from blueprints.home import home_bp

@home_bp.route('/')
def index():
    # Example data for dashboard
    recent_scans = [
        {
            'id': 1,
            'target': 'johndoe',
            'type': 'Username Search',
            'date': datetime(2025, 4, 5, 14, 30),
            'status': 'completed',
            'findings': 12
        },
        {
            'id': 2,
            'target': 'jane.smith@example.com',
            'type': 'Data Breach',
            'date': datetime(2025, 4, 5, 10, 15),
            'status': 'completed',
            'findings': 3
        },
        {
            'id': 3,
            'target': 'mikebrown',
            'type': 'AI Analysis',
            'date': datetime(2025, 4, 4, 16, 45),
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