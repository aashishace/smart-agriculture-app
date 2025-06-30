"""
Authentication Routes - Login, Register, Logout
"""

from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from flask_login import login_user, logout_user, login_required, current_user
from flask_babel import gettext as _
from app.models.user import User
from app import db
import re

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration."""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        phone = request.form.get('phone', '').strip()
        village = request.form.get('village', '').strip()
        state = request.form.get('state', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        language = request.form.get('language', 'hi')
        
        # Validation
        errors = []
        
        if not name or len(name) < 2:
            errors.append(_('Name must be at least 2 characters long'))
        
        # Phone number validation (Indian format)
        phone_pattern = r'^[6-9]\d{9}$'
        if not phone or not re.match(phone_pattern, phone):
            errors.append(_('Please enter a valid phone number (10 digits)'))
        
        # Check if phone already exists
        existing_user = User.query.filter_by(phone=phone).first()
        if existing_user:
            errors.append(_('This phone number is already registered'))
        
        if not password or len(password) < 6:
            errors.append(_('Password must be at least 6 characters long'))
        
        if password != confirm_password:
            errors.append(_('Passwords do not match'))
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('auth/register.html')
        
        # Create new user
        try:
            user = User(
                name=name,
                phone=phone,
                village=village,
                state=state,
                preferred_language=language
            )
            user.set_password(password)
            
            db.session.add(user)
            db.session.commit()
            
            # Auto-login the new user for better UX
            login_user(user, remember=True)
            user.update_last_login()
            
            flash(_('Welcome! Let\'s start by adding your farm.'), 'success')
            return redirect(url_for('main.onboarding'))
            
        except Exception as e:
            db.session.rollback()
            flash(_('Registration error occurred. Please try again.'), 'error')
            return render_template('auth/register.html')
    
    return render_template('auth/register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login."""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        phone = request.form.get('phone', '').strip()
        password = request.form.get('password', '')
        remember_me = bool(request.form.get('remember_me'))
        
        if not phone or not password:
            flash(_('Please enter phone number and password.'), 'error')
            return render_template('auth/login.html')
        
        # Find user by phone
        user = User.query.filter_by(phone=phone).first()
        
        if user and user.check_password(password):
            if user.is_active:
                login_user(user, remember=remember_me)
                user.update_last_login()
                
                # Set session language preference
                session['preferred_language'] = user.preferred_language
                
                # Redirect to intended page or dashboard
                next_page = request.args.get('next')
                if next_page:
                    return redirect(next_page)
                return redirect(url_for('main.dashboard'))
            else:
                flash(_('Your account is inactive. Please contact support.'), 'error')
        else:
            flash(_('Incorrect phone number or password.'), 'error')
    
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """User logout."""
    logout_user()
    flash(_('You have been logged out successfully.'), 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/profile')
@login_required
def profile():
    """User profile page."""
    return render_template('auth/profile.html', user=current_user)

@auth_bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """Edit user profile."""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        village = request.form.get('village', '').strip()
        state = request.form.get('state', '').strip()
        language = request.form.get('language', 'hi')
        
        # Validation
        if not name or len(name) < 2:
            flash(_('Name must be at least 2 characters long.'), 'error')
            return render_template('auth/edit_profile.html')
        
        try:
            current_user.name = name
            current_user.village = village
            current_user.state = state
            current_user.preferred_language = language
            
            db.session.commit()
            flash(_('Profile updated successfully.'), 'success')
            return redirect(url_for('auth.profile'))
            
        except Exception as e:
            db.session.rollback()
            flash(_('Error updating profile.'), 'error')
    
    return render_template('auth/edit_profile.html')

@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Change user password."""
    if request.method == 'POST':
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Validation
        if not current_user.check_password(current_password):
            flash(_('Current password is incorrect.'), 'error')
            return render_template('auth/change_password.html')
        
        if not new_password or len(new_password) < 6:
            flash(_('New password must be at least 6 characters long.'), 'error')
            return render_template('auth/change_password.html')
        
        if new_password != confirm_password:
            flash(_('New passwords do not match.'), 'error')
            return render_template('auth/change_password.html')
        
        try:
            current_user.set_password(new_password)
            db.session.commit()
            flash(_('Password changed successfully.'), 'success')
            return redirect(url_for('auth.profile'))
            
        except Exception as e:
            db.session.rollback()
            flash(_('Error changing password.'), 'error')
    
    return render_template('auth/change_password.html')
