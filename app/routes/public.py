"""
Public routes for FC-Advisor
"""

import hashlib
from datetime import date
from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from sqlalchemy import func
from app import db, limiter, csrf
from app.models import FC, Vote
from app.tags import get_all_tags, get_tag, get_random_tags

public_bp = Blueprint('public', __name__)


def get_voter_hash():
    """Generate a hash of the voter's IP for anonymous tracking"""
    from flask import current_app
    # Handle Docker/proxy: check X-Forwarded-For first
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    if ip:
        ip = ip.split(',')[0].strip()  # Get first IP if multiple
    else:
        ip = 'unknown'
    salt = current_app.config['SECRET_KEY']
    return hashlib.sha256(f"{ip}{salt}".encode()).hexdigest()


@public_bp.route('/')
def index():
    """Homepage with featured FCs"""
    # Get top 6 FCs by total votes
    top_fcs = db.session.query(
        FC,
        func.count(Vote.id).label('vote_count')
    ).outerjoin(Vote).group_by(FC.id).order_by(func.count(Vote.id).desc()).limit(6).all()
    
    all_tags = get_all_tags()
    
    return render_template('public/index.html', 
                         top_fcs=top_fcs, 
                         all_tags=all_tags)


@public_bp.route('/fcs')
def fc_list():
    """List all Fleet Commanders"""
    page = request.args.get('page', 1, type=int)
    per_page = 12
    
    # Get FCs with vote counts
    fcs_query = db.session.query(
        FC,
        func.count(Vote.id).label('vote_count')
    ).outerjoin(Vote).group_by(FC.id).order_by(func.count(Vote.id).desc())
    
    pagination = fcs_query.paginate(page=page, per_page=per_page, error_out=False)
    
    all_tags = get_all_tags()
    
    return render_template('public/fc_list.html', 
                         pagination=pagination,
                         all_tags=all_tags)


@public_bp.route('/fc/<int:fc_id>')
def fc_detail(fc_id):
    """FC detail page with voting"""
    fc = FC.query.get_or_404(fc_id)
    
    # Get tag counts for this FC
    tag_counts = fc.get_tag_counts()
    all_tags = get_all_tags()
    
    # Get random tags for voting (4 tags)
    random_tags = get_random_tags(4)
    
    # Check which tags the user already voted for today
    voter_hash = get_voter_hash()
    today = date.today()
    
    voted_tags = db.session.query(Vote.tag_id).filter(
        Vote.fc_id == fc_id,
        Vote.voter_hash == voter_hash,
        Vote.vote_date == today
    ).all()
    voted_tag_ids = [v[0] for v in voted_tags]
    
    return render_template('public/fc_detail.html',
                         fc=fc,
                         tag_counts=tag_counts,
                         all_tags=all_tags,
                         random_tags=random_tags,
                         voted_tag_ids=voted_tag_ids)


@public_bp.route('/fc/<int:fc_id>/vote', methods=['POST'])
@csrf.exempt  # Exempt from CSRF - protected by rate limiting and IP tracking
@limiter.limit("10 per minute")
def vote(fc_id):
    """Submit a vote for a FC"""
    fc = FC.query.get_or_404(fc_id)
    tag_id = request.form.get('tag_id')
    
    # Validate tag exists
    if not tag_id or not get_tag(tag_id):
        flash('Invalid tag.', 'error')
        return redirect(url_for('public.fc_detail', fc_id=fc_id))
    
    voter_hash = get_voter_hash()
    today = date.today()
    
    # Check if already voted for this tag today
    existing_vote = Vote.query.filter_by(
        fc_id=fc_id,
        tag_id=tag_id,
        voter_hash=voter_hash,
        vote_date=today
    ).first()
    
    if existing_vote:
        flash('You already voted for this badge today! Come back tomorrow 🌙', 'warning')
        return redirect(url_for('public.fc_detail', fc_id=fc_id))
    
    # Create the vote
    vote = Vote(
        fc_id=fc_id,
        tag_id=tag_id,
        voter_hash=voter_hash,
        vote_date=today
    )
    
    try:
        db.session.add(vote)
        db.session.commit()
        tag = get_tag(tag_id)
        flash(f'Vote recorded! {tag["emoji"]} {tag["name"]} for {fc.name} 🎉', 'success')
    except Exception:
        db.session.rollback()
        flash('Error while voting. Try again!', 'error')
    
    return redirect(url_for('public.fc_detail', fc_id=fc_id))


@public_bp.route('/fc/<int:fc_id>/refresh-tags')
def refresh_tags(fc_id):
    """Get new random tags (AJAX endpoint)"""
    fc = FC.query.get_or_404(fc_id)
    random_tags = get_random_tags(4)
    
    voter_hash = get_voter_hash()
    today = date.today()
    
    voted_tags = db.session.query(Vote.tag_id).filter(
        Vote.fc_id == fc_id,
        Vote.voter_hash == voter_hash,
        Vote.vote_date == today
    ).all()
    voted_tag_ids = [v[0] for v in voted_tags]
    
    return render_template('public/_voting_tags.html',
                         fc=fc,
                         random_tags=random_tags,
                         voted_tag_ids=voted_tag_ids)


@public_bp.route('/leaderboard')
def leaderboard():
    """Leaderboard page"""
    # Get all FCs with vote counts, sorted by total votes
    fcs = db.session.query(
        FC,
        func.count(Vote.id).label('vote_count')
    ).outerjoin(Vote).group_by(FC.id).order_by(func.count(Vote.id).desc()).all()
    
    # Get top tags overall
    top_tags = db.session.query(
        Vote.tag_id,
        func.count(Vote.id).label('count')
    ).group_by(Vote.tag_id).order_by(func.count(Vote.id).desc()).limit(10).all()
    
    all_tags = get_all_tags()
    
    return render_template('public/leaderboard.html',
                         fcs=fcs,
                         top_tags=top_tags,
                         all_tags=all_tags)
