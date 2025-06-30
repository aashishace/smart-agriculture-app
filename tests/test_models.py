"""
Unit tests for database models
"""

import pytest
from datetime import date, datetime
from app.models.user import User
from app.models.farm import Farm
from app.models.crop import Crop, Activity, DiseaseDetection
from app import db

class TestUserModel:
    """Test User model functionality."""
    
    def test_user_creation(self, app):
        """Test user creation."""
        with app.app_context():
            user = User(
                name='John Farmer',
                phone='9876543210',
                village='Test Village',
                state='Test State'
            )
            user.set_password('password123')
            
            assert user.name == 'John Farmer'
            assert user.phone == '9876543210'
            assert user.village == 'Test Village'
            assert user.state == 'Test State'
            assert user.preferred_language == 'hi'  # Default
            assert user.check_password('password123')
            assert not user.check_password('wrongpassword')
    
    def test_user_password_hashing(self, app):
        """Test password hashing."""
        with app.app_context():
            user = User(name='Test User', phone='1234567890')
            user.set_password('mypassword')
            
            # Password should be hashed, not stored as plaintext
            assert user.password_hash != 'mypassword'
            assert user.check_password('mypassword')
            assert not user.check_password('wrongpassword')
    
    def test_user_relationships(self, app, test_user):
        """Test user relationships."""
        with app.app_context():
            # test_user is now an ID, fetch the user object
            user = db.session.get(User, test_user)
            
            # Initially no farms
            assert user.get_farms_count() == 0
            assert user.get_active_crops_count() == 0
            
            # Add a farm
            farm = Farm(
                user_id=user.id,
                farm_name='Test Farm',
                area_acres=10.0,
                soil_type='Clay'
            )
            db.session.add(farm)
            db.session.commit()
            
            assert user.get_farms_count() == 1
    
    def test_user_to_dict(self, app, test_user):
        """Test user to_dict method."""
        with app.app_context():
            # test_user is now an ID, fetch the user object
            user = db.session.get(User, test_user)
            user_dict = user.to_dict()
            
            assert 'id' in user_dict
            assert 'name' in user_dict
            assert 'phone' in user_dict
            assert 'village' in user_dict
            assert 'state' in user_dict
            assert 'preferred_language' in user_dict
            assert 'farms_count' in user_dict
            assert 'active_crops_count' in user_dict
            
            assert user_dict['name'] == 'Test Farmer'
            assert user_dict['phone'] == '9876543210'

class TestFarmModel:
    """Test Farm model functionality."""
    
    def test_farm_creation(self, app, test_user):
        """Test farm creation."""
        with app.app_context():
            # test_user is now an ID, fetch the user object
            user = db.session.get(User, test_user)
            farm = Farm(
                user_id=user.id,
                farm_name='My Farm',
                area_acres=15.5,
                soil_type='Sandy Loam',
                latitude=28.6139,
                longitude=77.2090
            )
            
            assert farm.farm_name == 'My Farm'
            assert float(farm.area_acres) == 15.5
            assert farm.soil_type == 'Sandy Loam'
            assert float(farm.latitude) == 28.6139
            assert float(farm.longitude) == 77.2090
    
    def test_farm_location_methods(self, app, test_farm):
        """Test farm location-related methods."""
        with app.app_context():
            farm = db.session.get(Farm, test_farm)  # test_farm is now an ID
            
            # Test location getter
            location = farm.get_location()
            assert location == (28.6139, 77.2090)
            
            # Test location validation
            assert farm.is_location_set()
            
            # Test farm without location
            farm_no_location = Farm(
                user_id=farm.user_id,  # Use the fetched farm object
                farm_name='No Location Farm',
                area_acres=5.0
            )
            db.session.add(farm_no_location)
            db.session.commit()
            
            assert not farm_no_location.is_location_set()
            assert farm_no_location.get_location() is None
    
    def test_farm_area_calculations(self, app, test_farm):
        """Test farm area calculations."""
        with app.app_context():
            farm = db.session.get(Farm, test_farm)  # test_farm is now an ID
            
            # Initially no crops, so total crops area should be 0
            assert farm.get_total_crops_area() == 0
            assert farm.get_available_area() == 10.5
            
            # Add a crop
            crop = Crop(
                farm_id=farm.id,
                crop_type='wheat',
                area_acres=3.0,
                planting_date=date(2024, 11, 1)
            )
            db.session.add(crop)
            db.session.commit()
            
            assert farm.get_total_crops_area() == 3.0
            assert farm.get_available_area() == 7.5
    
    def test_farm_to_dict(self, app, test_farm):
        """Test farm to_dict method."""
        with app.app_context():
            farm = db.session.get(Farm, test_farm)  # test_farm is now an ID
            farm_dict = farm.to_dict()
            
            assert 'id' in farm_dict
            assert 'farm_name' in farm_dict
            assert 'area_acres' in farm_dict
            assert 'soil_type' in farm_dict
            assert 'latitude' in farm_dict
            assert 'longitude' in farm_dict
            assert 'active_crops_count' in farm_dict
            assert 'total_crops_area' in farm_dict
            assert 'available_area' in farm_dict
            
            assert farm_dict['farm_name'] == 'Test Farm'
            assert farm_dict['area_acres'] == 10.5

class TestCropModel:
    """Test Crop model functionality."""
    
    def test_crop_creation(self, app, test_farm):
        """Test crop creation."""
        with app.app_context():
            crop = Crop(
                farm_id=test_farm,  # test_farm is now an ID
                crop_type='rice',
                variety='Basmati',
                area_acres=4.0,
                planting_date=date(2024, 6, 15),
                current_stage='vegetative'
            )
            db.session.add(crop)
            db.session.flush()  # This applies defaults without committing
            
            assert crop.crop_type == 'rice'
            assert crop.variety == 'Basmati'
            assert float(crop.area_acres) == 4.0
            assert crop.planting_date == date(2024, 6, 15)
            assert crop.current_stage == 'vegetative'
            assert crop.status == 'active'  # Default
    
    def test_crop_days_calculations(self, app, test_crop):
        """Test crop days calculations."""
        with app.app_context():
            crop = db.session.get(Crop, test_crop)  # test_crop is now an ID
            
            # Test days since planting
            days_planted = crop.get_days_since_planting()
            assert isinstance(days_planted, int)
            assert days_planted >= 0
            
            # Test days to harvest (might be None if no expected harvest date)
            days_to_harvest = crop.get_days_to_harvest()
            # Could be None, int, or negative (past harvest)
    
    def test_crop_growth_stage_info(self, app, test_crop):
        """Test crop growth stage information."""
        with app.app_context():
            crop = db.session.get(Crop, test_crop)  # test_crop is now an ID
            stage_info = crop.get_growth_stage_info()
            
            assert isinstance(stage_info, dict)
            assert 'stage' in stage_info
            assert 'description' in stage_info
            
            # Should be a valid stage for wheat
            valid_stages = ['germination', 'tillering', 'jointing', 'flowering', 'grain_filling', 'maturity']
            assert stage_info['stage'] in valid_stages
    
    def test_crop_water_requirement(self, app, test_crop):
        """Test crop water requirement calculation."""
        with app.app_context():
            crop = db.session.get(Crop, test_crop)  # test_crop is now an ID
            water_req = crop.get_water_requirement()
            
            assert isinstance(water_req, (int, float))
            assert water_req > 0  # Should always be positive
            assert water_req <= 20  # Reasonable upper limit
    
    def test_crop_to_dict(self, app, test_crop):
        """Test crop to_dict method."""
        with app.app_context():
            crop = db.session.get(Crop, test_crop)  # test_crop is now an ID
            crop_dict = crop.to_dict()
            
            required_fields = [
                'id', 'farm_id', 'crop_type', 'variety', 'area_acres',
                'planting_date', 'current_stage', 'status',
                'days_since_planting', 'growth_stage_info', 'water_requirement'
            ]
            
            for field in required_fields:
                assert field in crop_dict
            
            assert crop_dict['crop_type'] == 'wheat'
            assert crop_dict['area_acres'] == 5.0

class TestActivityModel:
    """Test Activity model functionality."""
    
    def test_activity_creation(self, app, test_crop):
        """Test activity creation."""
        with app.app_context():
            activity = Activity(
                crop_id=test_crop,  # test_crop is now an ID
                activity_type='irrigation',
                description='Water the crops',
                quantity='5mm water',
                scheduled_date=date.today()
            )
            db.session.add(activity)
            db.session.flush()  # This applies defaults without committing
            
            assert activity.activity_type == 'irrigation'
            assert activity.description == 'Water the crops'
            assert activity.quantity == '5mm water'
            assert activity.status == 'pending'  # Default
    
    def test_activity_overdue_check(self, app, test_crop):
        """Test activity overdue checking."""
        with app.app_context():
            from datetime import timedelta
            
            # Create overdue activity
            overdue_activity = Activity(
                crop_id=test_crop,  # test_crop is now an ID
                activity_type='fertilizer',
                scheduled_date=date.today() - timedelta(days=2),
                status='pending'
            )
            db.session.add(overdue_activity)
            db.session.commit()
            
            assert overdue_activity.is_overdue()
            
            # Create future activity
            future_activity = Activity(
                crop_id=test_crop,  # test_crop is now an ID
                activity_type='irrigation',
                scheduled_date=date.today() + timedelta(days=2),
                status='pending'
            )
            db.session.add(future_activity)
            db.session.commit()
            
            assert not future_activity.is_overdue()
    
    def test_activity_completion(self, app, test_crop):
        """Test activity completion."""
        with app.app_context():
            activity = Activity(
                crop_id=test_crop,  # test_crop is now an ID
                activity_type='irrigation',
                scheduled_date=date.today(),
                status='pending'
            )
            db.session.add(activity)
            db.session.commit()
            
            # Mark as completed
            activity.mark_completed('Irrigation completed successfully')
            
            assert activity.status == 'completed'
            assert activity.completed_date == date.today()
            assert activity.notes == 'Irrigation completed successfully'

class TestDiseaseDetectionModel:
    """Test DiseaseDetection model functionality."""
    
    def test_disease_detection_creation(self, app, test_crop):
        """Test disease detection creation."""
        with app.app_context():
            detection = DiseaseDetection(
                crop_id=test_crop,  # test_crop is now an ID
                image_path='test_image.jpg',
                predicted_disease='Leaf Rust',
                confidence_score=0.85,
                treatment_suggested='Apply fungicide',
                is_healthy=False
            )
            
            assert detection.predicted_disease == 'Leaf Rust'
            assert float(detection.confidence_score) == 0.85
            assert detection.treatment_suggested == 'Apply fungicide'
            assert not detection.is_healthy
    
    def test_disease_detection_confidence_methods(self, app, test_crop):
        """Test confidence-related methods."""
        with app.app_context():
            detection = DiseaseDetection(
                crop_id=test_crop,  # test_crop is now an ID
                image_path='test_image.jpg',
                predicted_disease='Brown Spot',
                confidence_score=0.92,
                is_healthy=False
            )
            
            assert detection.get_confidence_percentage() == 92.0
            assert detection.is_high_confidence()  # > 80%
            
            # Test low confidence
            low_conf_detection = DiseaseDetection(
                crop_id=test_crop,  # test_crop is now an ID
                image_path='test_image2.jpg',
                predicted_disease='Unknown',
                confidence_score=0.65,
                is_healthy=False
            )
            
            assert low_conf_detection.get_confidence_percentage() == 65.0
            assert not low_conf_detection.is_high_confidence()  # <= 80%
    
    def test_disease_detection_to_dict(self, app, test_crop):
        """Test disease detection to_dict method."""
        with app.app_context():
            detection = DiseaseDetection(
                crop_id=test_crop,  # test_crop is now an ID
                image_path='test_image.jpg',
                predicted_disease='Leaf Rust',
                confidence_score=0.85,
                treatment_suggested='Apply fungicide',
                is_healthy=False
            )
            db.session.add(detection)
            db.session.commit()
            
            detection_dict = detection.to_dict()
            
            required_fields = [
                'id', 'crop_id', 'image_path', 'predicted_disease',
                'confidence_score', 'confidence_percentage', 'treatment_suggested',
                'is_healthy', 'is_high_confidence', 'detected_at'
            ]
            
            for field in required_fields:
                assert field in detection_dict
            
            assert detection_dict['predicted_disease'] == 'Leaf Rust'
            assert detection_dict['confidence_percentage'] == 85.0
            assert detection_dict['is_high_confidence']
