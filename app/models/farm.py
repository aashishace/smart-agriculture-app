"""
Farm Model - Represents farmer's land/farm
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from app import db

class Farm(db.Model):
    """Farm model representing a farmer's land."""
    
    __tablename__ = 'farms'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    farm_name = db.Column(db.String(100), nullable=False)
    area_acres = db.Column(db.Numeric(5, 2), nullable=False)
    soil_type = db.Column(db.String(50))
    latitude = db.Column(db.Numeric(10, 8))
    longitude = db.Column(db.Numeric(11, 8))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    crops = db.relationship('Crop', backref='farm', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Farm {self.farm_name} - {self.area_acres} acres>'
    
    def get_active_crops(self):
        """Get all active crops in this farm."""
        return self.crops.filter_by(status='active').all()
    
    def get_total_crops_area(self):
        """Calculate total area under crops."""
        from sqlalchemy import func
        from app.models.crop import Crop
        
        result = db.session.query(func.sum(Crop.area_acres)).filter(
            Crop.farm_id == self.id,
            Crop.status == 'active'
        ).scalar()
        
        return float(result) if result else 0.0
    
    def get_available_area(self):
        """Get available area for new crops."""
        return float(self.area_acres) - self.get_total_crops_area()
    
    def get_location(self):
        """Get farm location as tuple."""
        if self.latitude and self.longitude:
            return (float(self.latitude), float(self.longitude))
        return None
    
    def is_location_set(self):
        """Check if farm location is set."""
        return self.latitude is not None and self.longitude is not None
    
    def to_dict(self):
        """Convert farm to dictionary for JSON responses."""
        return {
            'id': self.id,
            'farm_name': self.farm_name,
            'area_acres': float(self.area_acres),
            'soil_type': self.soil_type,
            'latitude': float(self.latitude) if self.latitude else None,
            'longitude': float(self.longitude) if self.longitude else None,
            'active_crops_count': len(self.get_active_crops()),
            'total_crops_area': self.get_total_crops_area(),
            'available_area': self.get_available_area(),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
