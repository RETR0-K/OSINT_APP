# blueprints/auth/routes.py
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from urllib.parse import urlparse  # Use urllib.parse instead of werkzeug.urls
from datetime import datetime

from blueprints.auth import auth_bp
from models import db, User

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # If user is already logged in, redirect to home page
    if current_user.is_authenticated:
        return redirect(url_for('home.index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember_me = request.form.get('remember_me') == 'true'
        
        user = User.query.filter_by(username=username).first()
        
        # Check if user exists and password is correct
        if user is None or not user.verify_password(password):
            flash('Invalid username or password', 'error')
            return redirect(url_for('auth.login'))
        
        # Log in the user
        login_user(user, remember=remember_me)
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        # Redirect to the page the user was trying to access or to home
        next_page = request.args.get('next')
        if not next_page or urlparse(next_page).netloc != '':
            next_page = url_for('home.index')
        
        return redirect(next_page)
    
    return render_template('auth/login.html', now=datetime.now())

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    # If user is already logged in, redirect to home page
    if current_user.is_authenticated:
        return redirect(url_for('home.index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Simple validation
        if not all([username, email, password, confirm_password]):
            flash('All fields are required', 'error')
            return redirect(url_for('auth.register'))
        
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return redirect(url_for('auth.register'))
        
        # Check if username or email already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
            return redirect(url_for('auth.register'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already exists', 'error')
            return redirect(url_for('auth.register'))
        
        # Create new user
        new_user = User(username=username, email=email)
        new_user.password = password
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! You can now login.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', now=datetime.now())

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home.index'))

@auth_bp.route('/profile')
@login_required
def profile():
    """Display the user profile page"""
    return render_template('auth/profile.html', user=current_user, now=datetime.now())

@auth_bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """Edit user profile"""
    if request.method == 'POST':
        email = request.form.get('email')
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        # Check if email is already taken by another user
        if email != current_user.email:
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                flash('Email already in use by another account', 'error')
                return redirect(url_for('auth.edit_profile'))
            
            # Update email
            current_user.email = email
        
        # Update password if provided
        if current_password and new_password and confirm_password:
            # Verify current password
            if not current_user.verify_password(current_password):
                flash('Current password is incorrect', 'error')
                return redirect(url_for('auth.edit_profile'))
            
            # Check if new passwords match
            if new_password != confirm_password:
                flash('New passwords do not match', 'error')
                return redirect(url_for('auth.edit_profile'))
            
            # Update password
            current_user.password = new_password
        
        # Save changes
        db.session.commit()
        flash('Profile updated successfully', 'success')
        return redirect(url_for('auth.profile'))
    
    return render_template('auth/edit_profile.html', user=current_user, now=datetime.now())