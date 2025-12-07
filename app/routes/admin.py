"""
Admin routes for FC-Advisor
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from sqlalchemy import func
from app import db
from app.models import FC, Vote
from app.tags import get_all_tags

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/')
@login_required
def dashboard():
    """Admin dashboard with stats"""
    total_fcs = FC.query.count()
    total_votes = Vote.query.count()
    
    # Recent FCs
    recent_fcs = FC.query.order_by(FC.created_at.desc()).limit(5).all()
    
    # Top voted FCs
    top_fcs = db.session.query(
        FC,
        func.count(Vote.id).label('vote_count')
    ).outerjoin(Vote).group_by(FC.id).order_by(func.count(Vote.id).desc()).limit(5).all()
    
    return render_template('admin/dashboard.html',
                         total_fcs=total_fcs,
                         total_votes=total_votes,
                         recent_fcs=recent_fcs,
                         top_fcs=top_fcs)


@admin_bp.route('/fc/new', methods=['GET', 'POST'])
@login_required
def fc_create():
    """Create a new FC"""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        corporation = request.form.get('corporation', '').strip()
        alliance = request.form.get('alliance', '').strip()
        avatar_url = request.form.get('avatar_url', '').strip()
        bio = request.form.get('bio', '').strip()
        
        if not name:
            flash('FC name is required.', 'error')
            return render_template('admin/fc_form.html', fc=None)
        
        # Check if FC already exists
        if FC.query.filter_by(name=name).first():
            flash('An FC with this name already exists.', 'error')
            return render_template('admin/fc_form.html', fc=None)
        
        fc = FC(
            name=name,
            corporation=corporation,
            alliance=alliance,
            avatar_url=avatar_url,
            bio=bio
        )
        
        db.session.add(fc)
        db.session.commit()
        
        flash(f'FC "{name}" created successfully! 🎉', 'success')
        return redirect(url_for('admin.dashboard'))
    
    return render_template('admin/fc_form.html', fc=None)


@admin_bp.route('/fc/<int:fc_id>/edit', methods=['GET', 'POST'])
@login_required
def fc_edit(fc_id):
    """Edit an existing FC"""
    fc = FC.query.get_or_404(fc_id)
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        corporation = request.form.get('corporation', '').strip()
        alliance = request.form.get('alliance', '').strip()
        avatar_url = request.form.get('avatar_url', '').strip()
        bio = request.form.get('bio', '').strip()
        
        if not name:
            flash('FC name is required.', 'error')
            return render_template('admin/fc_form.html', fc=fc)
        
        # Check if another FC has this name
        existing = FC.query.filter_by(name=name).first()
        if existing and existing.id != fc.id:
            flash('Another FC with this name already exists.', 'error')
            return render_template('admin/fc_form.html', fc=fc)
        
        fc.name = name
        fc.corporation = corporation
        fc.alliance = alliance
        fc.avatar_url = avatar_url
        fc.bio = bio
        
        db.session.commit()
        
        flash(f'FC "{name}" updated! ✨', 'success')
        return redirect(url_for('admin.dashboard'))
    
    return render_template('admin/fc_form.html', fc=fc)


@admin_bp.route('/fc/<int:fc_id>/delete', methods=['POST'])
@login_required
def fc_delete(fc_id):
    """Delete a FC"""
    fc = FC.query.get_or_404(fc_id)
    name = fc.name
    
    db.session.delete(fc)
    db.session.commit()
    
    flash(f'FC "{name}" deleted. 💨', 'info')
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/fcs')
@login_required
def fc_list():
    """List all FCs for admin"""
    fcs = db.session.query(
        FC,
        func.count(Vote.id).label('vote_count')
    ).outerjoin(Vote).group_by(FC.id).order_by(FC.name).all()
    
    all_tags = get_all_tags()
    
    return render_template('admin/fc_list.html', fcs=fcs, all_tags=all_tags)


# ========== TAG MANAGEMENT ==========

@admin_bp.route('/tags')
@login_required
def tag_list():
    """List all tags for admin"""
    from app.models import Tag
    tags = Tag.query.order_by(Tag.name).all()
    return render_template('admin/tag_list.html', tags=tags)


@admin_bp.route('/tags/new', methods=['GET', 'POST'])
@login_required
def tag_create():
    """Create a new tag"""
    from app.models import Tag
    
    if request.method == 'POST':
        tag_id = request.form.get('id', '').strip().lower().replace(' ', '_')
        name = request.form.get('name', '').strip()
        emoji = request.form.get('emoji', '').strip()
        description = request.form.get('description', '').strip()
        
        if not tag_id or not name or not emoji:
            flash('ID, Name and Emoji are required.', 'error')
            return render_template('admin/tag_form.html', tag=None)
        
        # Check if tag already exists
        if Tag.query.get(tag_id):
            flash('A tag with this ID already exists.', 'error')
            return render_template('admin/tag_form.html', tag=None)
        
        tag = Tag(
            id=tag_id,
            name=name,
            emoji=emoji,
            description=description,
            is_active=True
        )
        
        db.session.add(tag)
        db.session.commit()
        
        flash(f'Badge "{name}" created! {emoji}', 'success')
        return redirect(url_for('admin.tag_list'))
    
    return render_template('admin/tag_form.html', tag=None)


@admin_bp.route('/tags/<tag_id>/edit', methods=['GET', 'POST'])
@login_required
def tag_edit(tag_id):
    """Edit an existing tag"""
    from app.models import Tag
    tag = Tag.query.get_or_404(tag_id)
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        emoji = request.form.get('emoji', '').strip()
        description = request.form.get('description', '').strip()
        is_active = request.form.get('is_active') == 'on'
        
        if not name or not emoji:
            flash('Name and Emoji are required.', 'error')
            return render_template('admin/tag_form.html', tag=tag)
        
        tag.name = name
        tag.emoji = emoji
        tag.description = description
        tag.is_active = is_active
        
        db.session.commit()
        
        flash(f'Badge "{name}" updated! ✨', 'success')
        return redirect(url_for('admin.tag_list'))
    
    return render_template('admin/tag_form.html', tag=tag)


@admin_bp.route('/tags/<tag_id>/delete', methods=['POST'])
@login_required
def tag_delete(tag_id):
    """Delete a tag"""
    from app.models import Tag
    tag = Tag.query.get_or_404(tag_id)
    name = tag.name
    
    db.session.delete(tag)
    db.session.commit()
    
    flash(f'Badge "{name}" deleted. 💨', 'info')
    return redirect(url_for('admin.tag_list'))


# ========== USER MANAGEMENT ==========

@admin_bp.route('/users')
@login_required
def user_list():
    """List all admin users"""
    from app.models import Admin
    users = Admin.query.order_by(Admin.username).all()
    return render_template('admin/user_list.html', users=users)


@admin_bp.route('/users/new', methods=['GET', 'POST'])
@login_required
def user_create():
    """Create a new admin user"""
    from app.models import Admin
    from werkzeug.security import generate_password_hash
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip().lower()
        password = request.form.get('password', '')
        confirm = request.form.get('confirm', '')
        
        if not username or not password:
            flash('Username and password are required.', 'error')
            return render_template('admin/user_form.html', user=None)
        
        if password != confirm:
            flash('Passwords do not match.', 'error')
            return render_template('admin/user_form.html', user=None)
        
        if len(password) < 8:
            flash('Password must be at least 8 characters.', 'error')
            return render_template('admin/user_form.html', user=None)
        
        if Admin.query.filter_by(username=username).first():
            flash('Username already exists.', 'error')
            return render_template('admin/user_form.html', user=None)
        
        user = Admin(
            username=username,
            password_hash=generate_password_hash(password)
        )
        
        db.session.add(user)
        db.session.commit()
        
        flash(f'User "{username}" created! 👤', 'success')
        return redirect(url_for('admin.user_list'))
    
    return render_template('admin/user_form.html', user=None)


@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
def user_delete(user_id):
    """Delete an admin user"""
    from app.models import Admin
    from flask_login import current_user
    
    user = Admin.query.get_or_404(user_id)
    
    # Can't delete yourself
    if user.id == current_user.id:
        flash("You can't delete your own account!", 'error')
        return redirect(url_for('admin.user_list'))
    
    username = user.username
    db.session.delete(user)
    db.session.commit()
    
    flash(f'User "{username}" deleted. 💨', 'info')
    return redirect(url_for('admin.user_list'))
