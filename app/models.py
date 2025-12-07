"""
Database models for FC-Advisor
"""

from datetime import datetime, date
from flask_login import UserMixin
from app import db, login_manager


class FC(db.Model):
    """Fleet Commander model"""
    __tablename__ = 'fc'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False, index=True)
    corporation = db.Column(db.String(100), default='')
    alliance = db.Column(db.String(100), default='')
    avatar_url = db.Column(db.String(500), default='')
    bio = db.Column(db.Text, default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship to votes
    votes = db.relationship('Vote', backref='fc', lazy='dynamic', cascade='all, delete-orphan')
    
    def get_tag_counts(self):
        """Get count of votes per tag for this FC"""
        from sqlalchemy import func
        results = db.session.query(
            Vote.tag_id, 
            func.count(Vote.id).label('count')
        ).filter(Vote.fc_id == self.id).group_by(Vote.tag_id).all()
        
        return {tag_id: count for tag_id, count in results}
    
    def get_total_votes(self):
        """Get total number of votes for this FC"""
        return self.votes.count()
    
    def __repr__(self):
        return f'<FC {self.name}>'


class Tag(db.Model):
    """Tag/Badge model for voting"""
    __tablename__ = 'tag'
    
    id = db.Column(db.String(50), primary_key=True)  # e.g., 'content_generator'
    name = db.Column(db.String(100), nullable=False)  # e.g., 'Content Generator'
    emoji = db.Column(db.String(10), nullable=False)  # e.g., '🎬'
    description = db.Column(db.String(200), default='')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Tag {self.id}>'
    
    def to_dict(self):
        return {
            'name': self.name,
            'emoji': self.emoji,
            'description': self.description
        }


class Vote(db.Model):
    """Vote model - represents a tag vote for a FC"""
    __tablename__ = 'vote'
    
    id = db.Column(db.Integer, primary_key=True)
    fc_id = db.Column(db.Integer, db.ForeignKey('fc.id'), nullable=False, index=True)
    tag_id = db.Column(db.String(50), nullable=False, index=True)
    voter_hash = db.Column(db.String(64), nullable=False, index=True)  # SHA256 hash of IP + salt
    vote_date = db.Column(db.Date, nullable=False, default=date.today)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Unique constraint: one vote per FC per tag per voter per day
    __table_args__ = (
        db.UniqueConstraint('fc_id', 'tag_id', 'voter_hash', 'vote_date', name='unique_vote_per_day'),
    )
    
    def __repr__(self):
        return f'<Vote {self.tag_id} for FC {self.fc_id}>'


class Admin(db.Model, UserMixin):
    """Admin user model"""
    __tablename__ = 'admin'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Admin {self.username}>'


@login_manager.user_loader
def load_user(user_id):
    """Load admin user for Flask-Login"""
    return Admin.query.get(int(user_id))
