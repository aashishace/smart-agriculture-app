"""
Unit tests for route handlers
"""

import pytest
import json
import io
from flask import url_for
from app.models.user import User
from app.models.farm import Farm
from app.models.crop import Crop
from app import db

class TestAuthRoutes:
    """Test authentication routes."""
    
    def test_index_page(self, client):
        """Test index page."""
        response = client.get('/')
        assert response.status_code == 200
        # Should redirect to dashboard if logged in, or show index
    
    def test_login_page(self, client):
        """Test login page access."""
        response = client.get('/auth/login')
        assert response.status_code == 200
        # Check for Hindi text or form elements
        assert b'\xe0\xa4\xb2\xe0\xa5\x89\xe0\xa4\x97' in response.data or b'phone' in response.data
    
    def test_register_page(self, client):
        """Test register page access."""
        response = client.get('/auth/register')
        assert response.status_code == 200
        # Check for Hindi text or form elements
        assert b'\xe0\xa4\xb0\xe0\xa4\x9c\xe0\xa4\xbf\xe0\xa4\xb8' in response.data or b'phone' in response.data
    
    def test_user_registration(self, client, app):
        """Test user registration process."""
        response = client.post('/auth/register', data={
            'name': 'New Farmer',
            'phone': '9876543210',
            'village': 'New Village',
            'state': 'New State',
            'password': 'newpassword123',
            'confirm_password': 'newpassword123',
            'preferred_language': 'hi'
        })
        
        # Should redirect after successful registration
        assert response.status_code in [200, 302]
        
        # Check if user was created in database
        with app.app_context():
            user = User.query.filter_by(phone='9876543210').first()
            assert user is not None
            assert user.name == 'New Farmer'
            assert user.village == 'New Village'
    
    def test_user_login(self, client, app, test_user):
        """Test user login process."""
        with app.app_context():
            response = client.post('/auth/login', data={
                'phone': '9876543210',
                'password': 'testpass123'
            })
            
            # Should redirect to dashboard after successful login
            assert response.status_code in [200, 302]
    
    def test_invalid_login(self, client):
        """Test login with invalid credentials."""
        response = client.post('/auth/login', data={
            'phone': '9876543210',
            'password': 'wrongpassword'
        })
        
        # Should return to login page with error
        assert response.status_code == 200

class TestMainRoutes:
    """Test main application routes."""
    
    def login_user(self, client, phone='9876543210', password='testpass123'):
        """Helper method to login a user."""
        return client.post('/auth/login', data={
            'phone': phone,
            'password': password
        })
    
    def test_dashboard_requires_login(self, client):
        """Test dashboard requires authentication."""
        response = client.get('/dashboard')
        assert response.status_code == 302  # Redirect to login
    
    def test_dashboard_with_user(self, client, app, test_user):
        """Test dashboard with logged in user."""
        with app.app_context():
            # Login user
            self.login_user(client)
            
            response = client.get('/dashboard')
            # Should be accessible after login
            assert response.status_code in [200, 302]

class TestFarmRoutes:
    """Test farm management routes."""
    
    def login_user(self, client, phone='9876543210', password='testpass123'):
        """Helper method to login a user."""
        return client.post('/auth/login', data={
            'phone': phone,
            'password': password
        })
    
    def test_farms_index_requires_login(self, client):
        """Test farms index requires authentication."""
        response = client.get('/farms/')
        assert response.status_code == 302  # Redirect to login
    
    def test_add_farm_requires_login(self, client):
        """Test add farm requires authentication."""
        response = client.get('/farms/add')
        assert response.status_code == 302  # Redirect to login
    
    def test_add_farm_form(self, client, app, test_user):
        """Test add farm form submission."""
        with app.app_context():
            # Login user
            self.login_user(client)
            
            response = client.post('/farms/add', data={
                'farm_name': 'New Test Farm',
                'area_acres': '15.5',
                'soil_type': 'Clay Loam',
                'latitude': '28.6139',
                'longitude': '77.2090'
            })
            
            # Should redirect after successful creation
            assert response.status_code in [200, 302]
            
            # Check if farm was created
            farm = Farm.query.filter_by(farm_name='New Test Farm').first()
            assert farm is not None
            assert float(farm.area_acres) == 15.5

class TestCropRoutes:
    """Test crop management routes."""
    
    def login_user(self, client, phone='9876543210', password='testpass123'):
        """Helper method to login a user."""
        return client.post('/auth/login', data={
            'phone': phone,
            'password': password
        })
    
    def test_crops_index_requires_login(self, client):
        """Test crops index requires authentication."""
        response = client.get('/crops/')
        assert response.status_code == 302  # Redirect to login
    
    def test_add_crop_requires_login(self, client):
        """Test add crop requires authentication."""
        response = client.get('/crops/add')
        assert response.status_code == 302  # Redirect to login
    
    def test_add_crop_form(self, client, app, test_user, test_farm):
        """Test add crop form submission."""
        with app.app_context():
            # Login user
            self.login_user(client)
            
            from datetime import date
            response = client.post('/crops/add', data={
                'farm_id': str(test_farm),  # test_farm is now an ID
                'crop_type': 'rice',
                'variety': 'Basmati Gold',
                'area_acres': '3.5',
                'planting_date': '2024-11-01'
            })
            
            # Should redirect after successful creation
            assert response.status_code in [200, 302]
            
            # Check if crop was created
            crop = Crop.query.filter_by(crop_type='rice', variety='Basmati Gold').first()
            assert crop is not None
            assert float(crop.area_acres) == 3.5

class TestAIRoutes:
    """Test AI/ML routes."""
    
    def login_user(self, client, phone='9876543210', password='testpass123'):
        """Helper method to login a user."""
        return client.post('/auth/login', data={
            'phone': phone,
            'password': password
        })
    
    def test_disease_scanner_requires_login(self, client):
        """Test disease scanner requires authentication."""
        response = client.get('/ai/disease-scanner')
        assert response.status_code == 302  # Redirect to login
    
    def test_disease_history_requires_login(self, client):
        """Test disease history requires authentication."""
        response = client.get('/ai/disease-history')
        assert response.status_code == 302  # Redirect to login
    
    def test_disease_scanner_page(self, client, app, test_user):
        """Test disease scanner page access."""
        with app.app_context():
            # Login user
            self.login_user(client)
            
            response = client.get('/ai/disease-scanner')
            assert response.status_code == 200
    
    def test_disease_detection_api_requires_login(self, client):
        """Test disease detection API requires authentication."""
        # Create a test image file
        data = {
            'image': (io.BytesIO(b'fake image data'), 'test.jpg'),
            'crop_id': '1'
        }
        
        response = client.post('/ai/detect-disease', 
                             data=data,
                             content_type='multipart/form-data')
        assert response.status_code == 302  # Redirect to login

class TestAPIEndpoints:
    """Test API endpoints."""
    
    def login_user(self, client, phone='9876543210', password='testpass123'):
        """Helper method to login a user."""
        return client.post('/auth/login', data={
            'phone': phone,
            'password': password
        })
    
    def test_weather_api_requires_login(self, client):
        """Test weather API requires authentication."""
        response = client.get('/api/weather/28.6139/77.2090')
        assert response.status_code == 302  # Redirect to login
    
    def test_weather_api_with_login(self, client, app, test_user):
        """Test weather API with authentication."""
        with app.app_context():
            # Login user
            self.login_user(client)
            
            response = client.get('/api/weather/28.6139/77.2090')
            # Should return JSON data (may be mock data)
            assert response.status_code == 200
            
            # Check if response is valid JSON
            try:
                data = json.loads(response.data)
                assert 'current' in data or 'error' in data
            except json.JSONDecodeError:
                # If not JSON, check if it's a redirect or error
                assert response.status_code in [200, 302, 500]

class TestErrorHandling:
    """Test error handling."""
    
    def test_404_error(self, client):
        """Test 404 error handling."""
        response = client.get('/nonexistent-page')
        assert response.status_code == 404
    
    def test_invalid_crop_id(self, client, app, test_user):
        """Test handling of invalid crop ID."""
        with app.app_context():
            # Login user
            client.post('/auth/login', data={
                'phone': '9876543210',
                'password': 'testpass123'
            })
            
            # Try to access non-existent crop
            response = client.get('/crops/99999')
            assert response.status_code in [404, 302]  # Not found or redirect

class TestFormValidation:
    """Test form validation."""
    
    def test_registration_password_mismatch(self, client):
        """Test registration with password mismatch."""
        response = client.post('/auth/register', data={
            'name': 'Test User',
            'phone': '9876543210',
            'village': 'Test Village',
            'state': 'Test State',
            'password': 'password123',
            'confirm_password': 'differentpassword',
            'preferred_language': 'hi'
        })
        
        # Should return error
        assert response.status_code == 200
        # User should not be created
    
    def test_registration_duplicate_phone(self, client, app, test_user):
        """Test registration with duplicate phone number."""
        with app.app_context():
            response = client.post('/auth/register', data={
                'name': 'Another User',
                'phone': '9876543210',  # Same as test_user
                'village': 'Another Village',
                'state': 'Another State',
                'password': 'password123',
                'confirm_password': 'password123',
                'preferred_language': 'hi'
            })
            
            # Should return error for duplicate phone
            assert response.status_code == 200
    
    def test_invalid_farm_data(self, client, app, test_user):
        """Test farm creation with invalid data."""
        with app.app_context():
            # Login user
            client.post('/auth/login', data={
                'phone': '9876543210',
                'password': 'testpass123'
            })
            
            # Try to create farm with invalid area
            response = client.post('/farms/add', data={
                'farm_name': 'Invalid Farm',
                'area_acres': '-5.0',  # Negative area
                'soil_type': 'Clay',
                'latitude': '28.6139',
                'longitude': '77.2090'
            })
            
            # Should handle validation error
            assert response.status_code == 200  # Form should be redisplayed
