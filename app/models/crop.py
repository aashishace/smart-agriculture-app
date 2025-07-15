"""
Crop Model - Represents crops planted on farms
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
from app import db

class Crop(db.Model):
    """Crop model representing crops planted on farms."""
    
    __tablename__ = 'crops'
    
    id = db.Column(db.Integer, primary_key=True)
    farm_id = db.Column(db.Integer, db.ForeignKey('farms.id'), nullable=False)
    crop_type = db.Column(db.String(50), nullable=False)
    variety = db.Column(db.String(50))
    area_acres = db.Column(db.Numeric(5, 2), nullable=False)
    planting_date = db.Column(db.Date, nullable=False)
    expected_harvest_date = db.Column(db.Date)
    current_stage = db.Column(db.String(50), default='germination')
    status = db.Column(db.String(20), default='active')  # active, harvested, failed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    activities = db.relationship('Activity', backref='crop', lazy='dynamic', cascade='all, delete-orphan')
    disease_detections = db.relationship('DiseaseDetection', backref='crop', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Crop {self.crop_type} - {self.variety}>'
    
    def get_days_since_planting(self):
        """Get number of days since planting."""
        if self.planting_date:
            return (date.today() - self.planting_date).days
        return 0
    
    def get_days_to_harvest(self):
        """Get number of days until expected harvest."""
        if self.expected_harvest_date:
            return (self.expected_harvest_date - date.today()).days
        return None
    
    def get_growth_stage_info(self):
        """Get detailed information about current growth stage from database."""
        from app.models.crop_data import CropInfo, GrowthStage
        
        days_planted = self.get_days_since_planting()
        
        crop_info = CropInfo.query.filter_by(name=self.crop_type.lower()).first()
        if not crop_info:
            return {'stage': 'unknown', 'description': 'अज्ञात'}
        
        current_stage = GrowthStage.query.filter(
            GrowthStage.crop_info_id == crop_info.id,
            GrowthStage.start_day <= days_planted,
            GrowthStage.end_day >= days_planted
        ).first()
        
        if current_stage:
            return {
                'stage': current_stage.stage_name,
                'description': current_stage.stage_description_hi
            }
        
        return {'stage': 'unknown', 'description': 'अज्ञात'}
    
    def get_recent_activities(self, limit=5):
        """Get recent activities for this crop."""
        return self.activities.order_by(Activity.scheduled_date.desc()).limit(limit).all()
    
    def get_water_requirement(self):
        """Get daily water requirement based on crop type and stage from database."""
        from app.models.crop_data import CropInfo, GrowthStage
        
        days_planted = self.get_days_since_planting()
        
        crop_info = CropInfo.query.filter_by(name=self.crop_type.lower()).first()
        if not crop_info:
            return 5  # Default value
        
        current_stage = GrowthStage.query.filter(
            GrowthStage.crop_info_id == crop_info.id,
            GrowthStage.start_day <= days_planted,
            GrowthStage.end_day >= days_planted
        ).first()
        
        if current_stage and current_stage.water_requirement_mm_day:
            return float(current_stage.water_requirement_mm_day)
        
        return 5  # Default value
    
    def to_dict(self):
        """Convert crop to dictionary for JSON responses."""
        stage_info = self.get_growth_stage_info()
        
        return {
            'id': self.id,
            'farm_id': self.farm_id,
            'crop_type': self.crop_type,
            'variety': self.variety,
            'area_acres': float(self.area_acres),
            'planting_date': self.planting_date.isoformat() if self.planting_date else None,
            'expected_harvest_date': self.expected_harvest_date.isoformat() if self.expected_harvest_date else None,
            'current_stage': self.current_stage,
            'status': self.status,
            'days_since_planting': self.get_days_since_planting(),
            'days_to_harvest': self.get_days_to_harvest(),
            'growth_stage_info': stage_info,
            'water_requirement': self.get_water_requirement(),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Activity(db.Model):
    """Activity model for farming activities (irrigation, fertilization, etc.)."""
    
    __tablename__ = 'activities'
    
    id = db.Column(db.Integer, primary_key=True)
    crop_id = db.Column(db.Integer, db.ForeignKey('crops.id'), nullable=False)
    activity_type = db.Column(db.String(50), nullable=False)  # irrigation, fertilizer, pesticide, etc.
    description = db.Column(db.Text)
    quantity = db.Column(db.String(50))  # e.g., "5mm water", "10kg urea"
    scheduled_date = db.Column(db.Date, nullable=False)
    completed_date = db.Column(db.Date)
    status = db.Column(db.String(20), default='pending')  # pending, completed, skipped
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Activity {self.activity_type} - {self.status}>'
    
    def is_overdue(self):
        """Check if activity is overdue."""
        if self.status == 'pending' and self.scheduled_date:
            return date.today() > self.scheduled_date
        return False
    
    def mark_completed(self, notes=None):
        """Mark activity as completed."""
        self.status = 'completed'
        self.completed_date = date.today()
        if notes:
            self.notes = notes
        db.session.commit()
    
    def to_dict(self):
        """Convert activity to dictionary for JSON responses."""
        return {
            'id': self.id,
            'crop_id': self.crop_id,
            'activity_type': self.activity_type,
            'description': self.description,
            'quantity': self.quantity,
            'scheduled_date': self.scheduled_date.isoformat() if self.scheduled_date else None,
            'completed_date': self.completed_date.isoformat() if self.completed_date else None,
            'status': self.status,
            'notes': self.notes,
            'is_overdue': self.is_overdue(),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class DiseaseDetection(db.Model):
    """Disease detection model for storing AI detection results."""
    
    __tablename__ = 'disease_detections'
    
    id = db.Column(db.Integer, primary_key=True)
    crop_id = db.Column(db.Integer, db.ForeignKey('crops.id'), nullable=False)
    image_path = db.Column(db.String(255), nullable=False)
    predicted_disease = db.Column(db.String(100))
    confidence_score = db.Column(db.Numeric(3, 2))  # 0.00 to 1.00
    treatment_suggested = db.Column(db.Text)
    is_healthy = db.Column(db.Boolean, default=False)
    detected_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<DiseaseDetection {self.predicted_disease} - {self.confidence_score}>'
    
    def get_confidence_percentage(self):
        """Get confidence score as percentage."""
        if self.confidence_score:
            return float(self.confidence_score) * 100
        return 0
    
    def is_high_confidence(self):
        """Check if detection has high confidence (>80%)."""
        return self.get_confidence_percentage() > 80
    
    def to_dict(self):
        """Convert detection to dictionary for JSON responses."""
        return {
            'id': self.id,
            'crop_id': self.crop_id,
            'image_path': self.image_path,
            'predicted_disease': self.predicted_disease,
            'confidence_score': float(self.confidence_score) if self.confidence_score else 0,
            'confidence_percentage': self.get_confidence_percentage(),
            'treatment_suggested': self.treatment_suggested,
            'is_healthy': self.is_healthy,
            'is_high_confidence': self.is_high_confidence(),
            'detected_at': self.detected_at.isoformat() if self.detected_at else None
        }
