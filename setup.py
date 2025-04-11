#!/usr/bin/env python
"""Setup script for creating the initial database and admin account"""

from app import create_app
from models import db, User
from datetime import datetime

def setup_database():
    """Initialize the database and create admin account"""
    print("Setting up OSINT Tracker database...")
    
    # Create the Flask app
    app = create_app()
    
    # Use app context to access the database
    with app.app_context():
        # Create all database tables
        db.create_all()
        print("Database tables created.")
        
        # Check if admin user already exists
        admin = User.query.filter_by(username='admin').first()
        if admin is None:
            # Create admin user
            admin = User(
                username='admin',
                email='admin@example.com',
                created_at=datetime.utcnow()
            )
            admin.password = 'admin123'  # This will be hashed by the model setter
            
            db.session.add(admin)
            db.session.commit()
            print("Admin user created with username 'admin' and password 'admin123'.")
            print("Please change the admin password after first login!")
        else:
            print("Admin user already exists.")
        
        print("Setup complete!")

if __name__ == "__main__":
    setup_database()