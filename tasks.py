# tasks.py
"""
Scheduled tasks for the OSINT Tracker application.
These tasks can be run with a scheduler like Celery or APScheduler,
or manually through a cron job that runs this script.
"""

import os
import sys
from datetime import datetime, timedelta
from app import create_app
from models import db, User, Scan

def clean_old_scans(days=30):
    """
    Remove scan data older than the specified number of days.
    This helps manage database size and protect user privacy.
    """
    app = create_app()
    
    with app.app_context():
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Find old scans
        old_scans = Scan.query.filter(Scan.scan_date < cutoff_date).all()
        count = len(old_scans)
        
        # Delete old scans
        for scan in old_scans:
            db.session.delete(scan)
        
        db.session.commit()
        
        print(f"Cleaned {count} scans older than {days} days.")

def send_inactive_user_reminders(days=60):
    """
    Send email reminders to users who haven't logged in for a while.
    """
    app = create_app()
    
    with app.app_context():
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Find inactive users
        inactive_users = User.query.filter(User.last_login < cutoff_date).all()
        
        for user in inactive_users:
            # Here you would send an email reminder
            # This is a placeholder - implement actual email sending logic
            print(f"Would send reminder to {user.username} ({user.email}) - inactive for {days} days")
            
        print(f"Found {len(inactive_users)} inactive users.")

def generate_user_reports():
    """
    Generate monthly security reports for users.
    """
    app = create_app()
    
    with app.app_context():
        # Get all active users
        users = User.query.all()
        
        for user in users:
            # Get user's scans from the past month
            one_month_ago = datetime.utcnow() - timedelta(days=30)
            recent_scans = Scan.query.filter_by(user_id=user.id).filter(Scan.scan_date > one_month_ago).all()
            
            if recent_scans:
                # Here you would generate and send a report
                # This is a placeholder - implement actual report generation logic
                print(f"Would generate report for {user.username} with {len(recent_scans)} recent scans")
        
        print(f"Processed reports for {len(users)} users.")

if __name__ == "__main__":
    # This allows running individual tasks from the command line
    # Example: python tasks.py clean_old_scans 90
    if len(sys.argv) > 1:
        task_name = sys.argv[1]
        
        if task_name == "clean_old_scans":
            days = int(sys.argv[2]) if len(sys.argv) > 2 else 30
            clean_old_scans(days)
        
        elif task_name == "send_inactive_user_reminders":
            days = int(sys.argv[2]) if len(sys.argv) > 2 else 60
            send_inactive_user_reminders(days)
        
        elif task_name == "generate_user_reports":
            generate_user_reports()
        
        else:
            print(f"Unknown task: {task_name}")
    else:
        print("Available tasks:")
        print("  clean_old_scans [days]")
        print("  send_inactive_user_reminders [days]")
        print("  generate_user_reports")