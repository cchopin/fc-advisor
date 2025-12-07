"""
Authentication routes
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required
from werkzeug.security import check_password_hash
from app.models import Admin

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Admin login page"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        if not username or not password:
            flash('Please fill in all fields.', 'error')
            return render_template('admin/login.html')
        
        admin = Admin.query.filter_by(username=username).first()
        
        if admin and check_password_hash(admin.password_hash, password):
            login_user(admin)
            flash('Login successful! Welcome, commander. 🚀', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('admin.dashboard'))
        
        flash('Invalid credentials.', 'error')
    
    return render_template('admin/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """Logout admin"""
    logout_user()
    flash('Logged out successfully. See you! 👋', 'info')
    return redirect(url_for('public.index'))
