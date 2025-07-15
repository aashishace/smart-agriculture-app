"""
New Models for Storing Crop and Disease Information
"""

from app import db

class CropInfo(db.Model):
    """Model to store general information about supported crop types."""
    
    __tablename__ = 'crop_info'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False, index=True)
    scientific_name = db.Column(db.String(100))
    description = db.Column(db.Text)
    avg_harvest_days = db.Column(db.Integer)
    
    # Relationships
    growth_stages = db.relationship('GrowthStage', backref='crop_info', lazy='dynamic', cascade='all, delete-orphan')
    diseases = db.relationship('DiseaseInfo', backref='crop_info', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<CropInfo {self.name}>'

class GrowthStage(db.Model):
    """Model to store growth stages for each crop."""
    
    __tablename__ = 'growth_stages'
    
    id = db.Column(db.Integer, primary_key=True)
    crop_info_id = db.Column(db.Integer, db.ForeignKey('crop_info.id'), nullable=False)
    stage_name = db.Column(db.String(50), nullable=False)
    stage_description_hi = db.Column(db.String(100))
    start_day = db.Column(db.Integer, nullable=False)
    end_day = db.Column(db.Integer, nullable=False)
    water_requirement_mm_day = db.Column(db.Numeric(4, 2))
    
    def __repr__(self):
        return f'<GrowthStage {self.stage_name} for crop {self.crop_info_id}>'

class DiseaseInfo(db.Model):
    """Model to store information about diseases for each crop."""
    
    __tablename__ = 'disease_info'
    
    id = db.Column(db.Integer, primary_key=True)
    crop_info_id = db.Column(db.Integer, db.ForeignKey('crop_info.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    name_hi = db.Column(db.String(100))
    symptoms = db.Column(db.Text)
    severity = db.Column(db.String(20)) # low, medium, high
    probability = db.Column(db.Numeric(3, 2)) # 0.00 to 1.00
    
    # Treatment Information
    treatment_immediate = db.Column(db.Text)
    treatment_chemical = db.Column(db.Text)
    treatment_organic = db.Column(db.Text)
    treatment_frequency = db.Column(db.String(100))
    treatment_precautions = db.Column(db.Text)
    
    def __repr__(self):
        return f'<DiseaseInfo {self.name} for crop {self.crop_info_id}>'


class CropHealthTip(db.Model):
    """Model to store general health tips for different crops."""
    
    __tablename__ = 'crop_health_tips'
    
    id = db.Column(db.Integer, primary_key=True)
    crop_name = db.Column(db.String(50), nullable=False, index=True)
    tip_category = db.Column(db.String(50)) # e.g., 'Irrigation', 'Fertilization', 'General'
    tip_en = db.Column(db.Text, nullable=False)
    tip_hi = db.Column(db.Text, nullable=False)
    
    def __repr__(self):
        return f'<CropHealthTip for {self.crop_name}>'
