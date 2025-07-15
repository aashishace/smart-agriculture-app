"""
Pytest configuration for Smart Crop Care Assistant.
"""

import pytest
import os
import tempfile
from app import create_app, db
from app.models.user import User
from app.models.farm import Farm
from app.models.crop import Crop
from app.models.crop_data import CropInfo, GrowthStage

@pytest.fixture
def app():
    """Create application for testing."""
    # Create a temporary database file
    db_fd, db_path = tempfile.mkstemp()
    
    app = create_app('testing')
    app.config['DATABASE'] = db_path
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.app_context():
        db.create_all()
        populate_crop_data(app)
        yield app
        db.drop_all()
    
    os.close(db_fd)
    os.unlink(db_path)

def populate_crop_data(app):
    """Populate the database with initial crop data for tests."""
    with app.app_context():
        wheat = CropInfo(name='wheat', avg_harvest_days=140)
        db.session.add(wheat)
        db.session.commit()
        
        wheat_stages = [
            GrowthStage(crop_info_id=wheat.id, stage_name='germination', stage_description_hi='अंकुरण', start_day=0, end_day=7, water_requirement_mm_day=2),
            GrowthStage(crop_info_id=wheat.id, stage_name='tillering', stage_description_hi='कल्ले निकलना', start_day=8, end_day=40, water_requirement_mm_day=4),
            GrowthStage(crop_info_id=wheat.id, stage_name='jointing', stage_description_hi='गांठ बनना', start_day=41, end_day=70, water_requirement_mm_day=6),
            GrowthStage(crop_info_id=wheat.id, stage_name='flowering', stage_description_hi='फूल आना', start_day=71, end_day=100, water_requirement_mm_day=6),
            GrowthStage(crop_info_id=wheat.id, stage_name='grain_filling', stage_description_hi='दाना भरना', start_day=101, end_day=120, water_requirement_mm_day=5),
            GrowthStage(crop_info_id=wheat.id, stage_name='maturity', stage_description_hi='पकना', start_day=121, end_day=140, water_requirement_mm_day=2)
        ]
        db.session.bulk_save_objects(wheat_stages)
        db.session.commit()

@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """Create test runner."""
    return app.test_cli_runner()

@pytest.fixture
def test_user(app):
    """Create test user that works across app contexts."""
    with app.app_context():
        user = User(
            name='Test Farmer',
            phone='9876543210',
            village='Test Village',
            state='Test State',
            preferred_language='hi'
        )
        user.set_password('testpass123')
        db.session.add(user)
        db.session.commit()
        
        # Get the user ID and return a function that fetches fresh instances
        user_id = user.id
        return user_id  # Return ID instead of object

@pytest.fixture
def test_farm(app, test_user):
    """Create test farm."""
    with app.app_context():
        # test_user is now an ID, so fetch the user object
        user = db.session.get(User, test_user)
        
        farm = Farm(
            user_id=user.id,
            farm_name='Test Farm',
            area_acres=10.5,
            soil_type='Loamy',
            latitude=28.6139,
            longitude=77.2090
        )
        db.session.add(farm)
        db.session.commit()
        
        farm_id = farm.id
        return farm_id  # Return ID instead of object

@pytest.fixture
def test_crop(app, test_farm):
    """Create test crop."""
    with app.app_context():
        from datetime import datetime, timedelta
        
        # test_farm is now an ID, so fetch the farm object
        farm = db.session.get(Farm, test_farm)
        
        crop = Crop(
            farm_id=farm.id,
            crop_type='wheat',
            variety='HD-2967',
            planting_date=datetime.now().date() - timedelta(days=30),
            area_acres=5.0,
            current_stage='vegetative'
        )
        db.session.add(crop)
        db.session.commit()
        
        crop_id = crop.id
        return crop_id  # Return ID instead of object
