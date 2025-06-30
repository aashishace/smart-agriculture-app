"""
User Model - Handles farmer user accounts
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone
from app import db

class User(UserMixin, db.Model):
    """User model for farmers."""
    
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(15), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=True, index=True)  # Optional email
    village = db.Column(db.String(100))
    state = db.Column(db.String(50))
    preferred_language = db.Column(db.String(10), default='hi')  # Hindi default
    password_hash = db.Column(db.String(255))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    last_login = db.Column(db.DateTime)
    
    # Relationships
    farms = db.relationship('Farm', backref='owner', lazy='dynamic', cascade='all, delete-orphan')
    
    def __init__(self, **kwargs):
        """Initialize user with default values."""
        # Set defaults if not provided
        if 'preferred_language' not in kwargs:
            kwargs['preferred_language'] = 'hi'
        super(User, self).__init__(**kwargs)
    
    def __repr__(self):
        return f'<User {self.name} - {self.phone}>'
    
    def set_password(self, password):
        """Hash and set password."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if provided password matches hash."""
        return check_password_hash(self.password_hash, password)
    
    def get_farms_count(self):
        """Get total number of farms."""
        return self.farms.count()
    
    def get_active_crops_count(self):
        """Get total number of active crops across all farms."""
        from app.models.crop import Crop
        from app.models.farm import Farm
        return Crop.query.join(Farm).filter(
            Farm.user_id == self.id,
            Crop.status == 'active'
        ).count()
    
    def update_last_login(self):
        """Update last login timestamp."""
        self.last_login = datetime.now(timezone.utc)
        db.session.commit()
    
    def to_dict(self):
        """Convert user to dictionary for JSON responses."""
        return {
            'id': self.id,
            'name': self.name,
            'phone': self.phone,
            'village': self.village,
            'state': self.state,
            'preferred_language': self.preferred_language,
            'farms_count': self.get_farms_count(),
            'active_crops_count': self.get_active_crops_count(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }
    
    @property
    def username(self):
        """Compatibility property for templates expecting username."""
        return self.name
    
    @username.setter
    def username(self, value):
        """Allow setting username to update name."""
        self.name = value
