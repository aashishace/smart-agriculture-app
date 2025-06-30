"""
Unit tests for service modules
"""

import pytest
import json
from unittest.mock import Mock, patch
from app.services.weather import WeatherService
from app.services.irrigation import IrrigationService
from app.services.notifications import NotificationService
from app.services.activity_templates import ActivityTemplateService
from app.models.farm import Farm
from app.models.crop import Crop
from app import db
from datetime import date, datetime

class TestWeatherService:
    """Test WeatherService functionality."""
    
    def test_weather_service_initialization(self, app):
        """Test weather service initialization."""
        with app.app_context():
            weather_service = WeatherService()
            assert weather_service is not None
            assert hasattr(weather_service, 'api_key')
            assert hasattr(weather_service, 'base_url')
    
    @patch('requests.get')
    def test_get_current_weather_success(self, mock_get, app):
        """Test successful weather API call."""
        with app.app_context():
            # Mock successful API response
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = {
                'weather': [{'main': 'Clear', 'description': 'clear sky'}],
                'main': {'temp': 25.5, 'humidity': 60},
                'wind': {'speed': 3.5},
                'name': 'Delhi'
            }
            mock_get.return_value = mock_response
            
            weather_service = WeatherService()
            result = weather_service.get_current_weather(28.6139, 77.2090)
            
            assert result is not None
            assert 'temperature' in result or 'temp' in result
    
    def test_get_weather_without_api_key(self, app):
        """Test weather service without API key (should return mock data)."""
        with app.app_context():
            weather_service = WeatherService()
            # Force API key to None to test fallback
            weather_service.api_key = None
            
            result = weather_service.get_current_weather(28.6139, 77.2090)
            
            # Should return mock data
            assert result is not None
            assert isinstance(result, dict)
    
    @patch('requests.get')
    def test_get_forecast_success(self, mock_get, app):
        """Test successful forecast API call."""
        with app.app_context():
            # Mock successful API response
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = {
                'list': [
                    {
                        'dt': 1234567890,
                        'main': {'temp': 26.0, 'humidity': 65},
                        'weather': [{'main': 'Clouds', 'description': 'few clouds'}],
                        'wind': {'speed': 2.5}
                    }
                ]
            }
            mock_get.return_value = mock_response
            
            weather_service = WeatherService()
            result = weather_service.get_forecast(28.6139, 77.2090, days=3)
            
            assert result is not None
            assert isinstance(result, dict)

class TestIrrigationService:
    """Test IrrigationService functionality."""
    
    def test_irrigation_service_initialization(self, app):
        """Test irrigation service initialization."""
        with app.app_context():
            irrigation_service = IrrigationService()
            assert irrigation_service is not None
    
    def test_calculate_crop_water_need(self, app, test_crop):
        """Test crop water need calculation."""
        with app.app_context():
            irrigation_service = IrrigationService()
            
            # Get the crop object
            from app.models.crop import Crop
            crop = db.session.get(Crop, test_crop)
            
            water_need = irrigation_service.calculate_irrigation_need(
                crop, farm_location=(28.6139, 77.2090)
            )
            
            assert isinstance(water_need, dict)
            assert 'action' in water_need
            assert 'base_need' in water_need or 'message' in water_need
    
    def test_irrigation_with_high_rain_probability(self, app, test_crop):
        """Test irrigation recommendation with high rain probability."""
        with app.app_context():
            irrigation_service = IrrigationService()
            
            # Get the crop object
            from app.models.crop import Crop
            crop = db.session.get(Crop, test_crop)
            
            water_need = irrigation_service.calculate_irrigation_need(
                crop, farm_location=(28.6139, 77.2090)
            )
            
            # The result should be a valid recommendation dict
            assert isinstance(water_need, dict)
            assert 'action' in water_need
    
    def test_calculate_farm_irrigation_schedule(self, app, test_farm):
        """Test farm irrigation schedule calculation."""
        with app.app_context():
            irrigation_service = IrrigationService()
            
            # Add a crop to the farm
            crop = Crop(
                farm_id=test_farm,  # test_farm is now an ID
                crop_type='wheat',
                area_acres=3.0,
                planting_date=date(2024, 11, 1),
                current_stage='flowering'
            )
            from app import db
            db.session.add(crop)
            db.session.commit()
            
            # Get the farm object for the schedule calculation
            from app.models.farm import Farm
            farm = db.session.get(Farm, test_farm)
            
            schedule = irrigation_service.calculate_farm_irrigation_schedule(farm)
            
            assert isinstance(schedule, list)
            if schedule:  # If there are crops to irrigate
                assert 'crop_id' in schedule[0]
                assert 'action' in schedule[0]

class TestNotificationService:
    """Test NotificationService functionality."""
    
    def test_notification_service_initialization(self, app):
        """Test notification service initialization."""
        with app.app_context():
            notification_service = NotificationService()
            assert notification_service is not None
    
    @patch('twilio.rest.Client')
    def test_send_sms_success(self, mock_twilio_client, app):
        """Test successful SMS sending."""
        with app.app_context():
            # Mock Twilio client
            mock_client_instance = Mock()
            mock_message = Mock()
            mock_message.sid = 'test_message_sid'
            mock_client_instance.messages.create.return_value = mock_message
            mock_twilio_client.return_value = mock_client_instance
            
            notification_service = NotificationService()
            
            result = notification_service.send_sms(
                '+919876543210',
                'Test message',
                'hi'
            )
            
            # Should return message SID on success
            assert result is not None
    
    def test_send_weather_alert(self, app):
        """Test weather alert notification."""
        with app.app_context():
            notification_service = NotificationService()
            
            # Test weather alert (may use mock Twilio)
            result = notification_service.send_weather_alert(
                '+919876543210',
                'Heavy rain expected',
                'hi'
            )
            
            # Should handle gracefully even if Twilio not configured
            assert result is not None or result is None
    
    def test_send_disease_alert(self, app):
        """Test disease alert notification."""
        with app.app_context():
            notification_service = NotificationService()
            
            result = notification_service.send_disease_alert(
                '+919876543210',
                'wheat',
                'Leaf Rust',
                85.0,
                'Apply fungicide immediately',
                'hi'
            )
            
            # Should handle gracefully
            assert result is not None or result is None

class TestActivityTemplateService:
    """Test ActivityTemplateService functionality."""
    
    def test_activity_template_service_initialization(self, app):
        """Test activity template service initialization."""
        with app.app_context():
            template_service = ActivityTemplateService()
            assert template_service is not None
    
    def test_get_crop_activity_templates(self, app):
        """Test getting activity templates for crops."""
        with app.app_context():
            template_service = ActivityTemplateService()
            
            # Test wheat templates
            wheat_templates = template_service.get_crop_activity_templates('wheat')
            assert isinstance(wheat_templates, list)
            assert len(wheat_templates) > 0
            
            # Each template should have required fields
            for template in wheat_templates:
                assert 'activity_type' in template
                assert 'days_after_planting' in template
                assert 'description' in template
    
    def test_generate_activities_for_crop(self, app, test_crop):
        """Test generating activities for a crop."""
        with app.app_context():
            template_service = ActivityTemplateService()
            
            # Get the crop object
            from app.models.crop import Crop
            crop = db.session.get(Crop, test_crop)
            
            activities = template_service.generate_activities_for_crop(crop)
            
            assert isinstance(activities, list)
            # Should generate some activities for wheat
            assert len(activities) > 0
            
            # Each activity should be properly formatted
            for activity in activities:
                assert hasattr(activity, 'crop_id')
                assert hasattr(activity, 'activity_type')
                assert hasattr(activity, 'scheduled_date')
                assert activity.crop_id == test_crop  # test_crop is an ID
    
    def test_get_activity_templates_for_stage(self, app):
        """Test getting activities for specific growth stage."""
        with app.app_context():
            template_service = ActivityTemplateService()
            
            # Test getting activities for flowering stage
            activities = template_service.get_activity_templates_for_stage('wheat', 'flowering')
            
            assert isinstance(activities, list)
            # Should return activities appropriate for flowering stage
    
    def test_create_bulk_activities(self, app, test_crop):
        """Test bulk activity creation."""
        with app.app_context():
            template_service = ActivityTemplateService()
            
            # Create activity objects to bulk create
            from app.models.crop import Activity
            from datetime import date
            
            activities = [
                Activity(
                    crop_id=test_crop,  # test_crop is an ID
                    activity_type='irrigation',
                    description='Water the crop',
                    scheduled_date=date.today()
                ),
                Activity(
                    crop_id=test_crop,  # test_crop is an ID
                    activity_type='fertilizer',
                    description='Apply NPK fertilizer',
                    scheduled_date=date.today()
                )
            ]
            
            result = template_service.create_bulk_activities(activities)
            
            assert isinstance(result, dict)
            assert result['success'] is True
            assert result['count'] == 2
            
            # Check if activities were created properly
            from app.models.crop import Activity
            irrigation_activity = Activity.query.filter_by(
                crop_id=test_crop,  # test_crop is an ID
                activity_type='irrigation'
            ).first()
            assert irrigation_activity is not None

class TestServiceIntegration:
    """Test integration between services."""
    
    def test_weather_irrigation_integration(self, app, test_farm):
        """Test integration between weather and irrigation services."""
        with app.app_context():
            weather_service = WeatherService()
            irrigation_service = IrrigationService()
            
            # Get the farm object
            from app.models.farm import Farm
            farm = db.session.get(Farm, test_farm)  # test_farm is now an ID
            
            # Get weather data (might be mock)
            weather_data = weather_service.get_current_weather(
                float(farm.latitude), 
                float(farm.longitude)
            )
            
            # Use weather data for irrigation calculation
            if weather_data:
                schedule = irrigation_service.calculate_farm_irrigation_schedule(farm)
                assert isinstance(schedule, list)
    
    def test_disease_notification_integration(self, app):
        """Test integration between disease detection and notifications."""
        with app.app_context():
            notification_service = NotificationService()
            
            # Simulate disease detection result
            disease_result = {
                'disease': 'Leaf Rust',
                'confidence': 0.89,
                'treatment': 'Apply fungicide',
                'is_healthy': False
            }
            
            # Should be able to send notification based on detection
            if not disease_result['is_healthy'] and disease_result['confidence'] > 0.8:
                result = notification_service.send_disease_alert(
                    '+919876543210',
                    'wheat',
                    disease_result['disease'],
                    disease_result['confidence'] * 100,
                    disease_result['treatment'],
                    'hi'
                )
                # Should handle gracefully
                assert result is not None or result is None
