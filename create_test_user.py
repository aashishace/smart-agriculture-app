#!/usr/bin/env python3
"""
Create a test user for development
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.user import User
from app.models.farm import Farm
from app.models.crop import Crop, Activity, DiseaseDetection
from datetime import datetime, timedelta, date
import random

def create_test_user():
    """Create a test user with comprehensive sample data."""
    app = create_app('development')
    
    with app.app_context():
        # Check if test user already exists
        existing_user = User.query.filter_by(phone='9876543210').first()
        if existing_user:
            print("Test user already exists!")
            # Delete existing data to recreate with fresh data
            print("Refreshing data with comprehensive sample...")
            
            # Delete existing crops and farms
            for farm in existing_user.farms:
                db.session.delete(farm)
            db.session.commit()
            
            user = existing_user
        else:
            # Create test user
            user = User(
                name='राम किसान',
                phone='9876543210',
                email='test@example.com',
                village='टेस्ट गांव',
                state='उत्तर प्रदेश',
                preferred_language='hi'
            )
            user.set_password('password123')
            
            db.session.add(user)
            db.session.commit()
        
        # Create multiple farms with realistic data
        farms_data = [
            {
                'farm_name': 'मुख्य खेत',
                'area_acres': 8.5,
                'soil_type': 'दोमट',
                'latitude': 26.8467,
                'longitude': 80.9462
            },
            {
                'farm_name': 'नदी के किनारे का खेत',
                'area_acres': 5.2,
                'soil_type': 'काली मिट्टी',
                'latitude': 26.8500,
                'longitude': 80.9500
            },
            {
                'farm_name': 'पहाड़ी खेत',
                'area_acres': 3.8,
                'soil_type': 'लाल मिट्टी',
                'latitude': 26.8400,
                'longitude': 80.9400
            }
        ]
        
        farms = []
        for farm_data in farms_data:
            farm = Farm(
                user_id=user.id,
                **farm_data
            )
            db.session.add(farm)
            farms.append(farm)
        
        db.session.commit()
        
        # Create diverse crops across farms with realistic timing
        crops_data = [
            # Farm 1 - Main farm (मुख्य खेत)
            {
                'farm': farms[0],
                'crop_type': 'गेहूं',
                'variety': 'HD-2967',
                'planting_date': date(2024, 11, 15),  # Nov planting
                'expected_harvest_date': date(2025, 4, 15),  # April harvest
                'area_acres': 3.0,
                'current_stage': 'flowering',
                'status': 'active'
            },
            {
                'farm': farms[0],
                'crop_type': 'सरसों',
                'variety': 'पूसा बोल्ड',
                'planting_date': date(2024, 10, 20),
                'expected_harvest_date': date(2025, 3, 20),
                'area_acres': 2.5,
                'current_stage': 'pod_formation',
                'status': 'active'
            },
            {
                'farm': farms[0],
                'crop_type': 'आलू',
                'variety': 'कुफरी ज्योति',
                'planting_date': date(2024, 12, 1),
                'expected_harvest_date': date(2025, 3, 15),
                'area_acres': 2.0,
                'current_stage': 'tuber_development',
                'status': 'active'
            },
            
            # Farm 2 - River side farm (नदी के किनारे का खेत)
            {
                'farm': farms[1],
                'crop_type': 'चावल',
                'variety': 'बासमती 1121',
                'planting_date': date(2024, 6, 15),  # Kharif season
                'expected_harvest_date': date(2024, 11, 15),
                'area_acres': 3.5,
                'current_stage': 'harvested',
                'status': 'harvested'
            },
            {
                'farm': farms[1],
                'crop_type': 'मक्का',
                'variety': 'हाईब्रिड-123',
                'planting_date': date(2024, 7, 1),
                'expected_harvest_date': date(2024, 11, 1),
                'area_acres': 1.7,
                'current_stage': 'harvested',
                'status': 'harvested'
            },
            
            # Farm 3 - Hill farm (पहाड़ी खेत)
            {
                'farm': farms[2],
                'crop_type': 'गन्ना',
                'variety': 'को-238',
                'planting_date': date(2024, 3, 1),
                'expected_harvest_date': date(2025, 2, 1),
                'area_acres': 2.0,
                'current_stage': 'maturation',
                'status': 'active'
            },
            {
                'farm': farms[2],
                'crop_type': 'अरहर',
                'variety': 'ICPL-87119',
                'planting_date': date(2024, 6, 20),
                'expected_harvest_date': date(2025, 1, 20),
                'area_acres': 1.8,
                'current_stage': 'pod_filling',
                'status': 'active'
            }
        ]
        
        crops = []
        for crop_data in crops_data:
            farm = crop_data.pop('farm')
            crop = Crop(
                farm_id=farm.id,
                **crop_data
            )
            db.session.add(crop)
            crops.append(crop)
        
        db.session.commit()
        
        # Create comprehensive activities for all crops
        print("Creating realistic farming activities...")
        
        activity_types = [
            'बुवाई', 'सिंचाई', 'खाद डालना', 'कीटनाशक छिड़काव', 
            'निराई-गुड़ाई', 'उर्वरक प्रयोग', 'रोग नियंत्रण', 'कटाई'
        ]
        
        # Generate activities for each crop
        for crop in crops:
            # Calculate number of days since planting
            days_since_planting = (date.today() - crop.planting_date).days
            
            # Create activities based on crop stage and time
            activities = []
            
            # Planting activity
            activities.append({
                'activity_type': 'बुवाई',
                'description': f'{crop.crop_type} की बुवाई - {crop.variety}',
                'scheduled_date': crop.planting_date,
                'status': 'completed',
                'quantity': '25 किग्रा/एकड़',
                'notes': 'बीज दर अनुसार बुवाई'
            })
            
            # Regular irrigation (every 15-20 days)
            irrigation_dates = []
            current_date = crop.planting_date + timedelta(days=10)
            while current_date < date.today() and current_date < crop.expected_harvest_date:
                irrigation_dates.append(current_date)
                current_date += timedelta(days=random.randint(15, 20))
            
            for i, irr_date in enumerate(irrigation_dates):
                activities.append({
                    'activity_type': 'सिंचाई',
                    'description': f'सिंचाई #{i+1}',
                    'scheduled_date': irr_date,
                    'status': 'completed' if irr_date <= date.today() else 'pending',
                    'quantity': f'{random.randint(2, 4)} घंटे',
                    'notes': f'पानी की आवश्यकता अनुसार'
                })
            
            # Fertilizer applications
            if days_since_planting > 30:
                activities.append({
                    'activity_type': 'खाद डालना',
                    'description': 'यूरिया और DAP का प्रयोग',
                    'scheduled_date': crop.planting_date + timedelta(days=30),
                    'status': 'completed',
                    'quantity': 'यूरिया: 50 किग्रा, DAP: 25 किग्रा',
                    'notes': 'पहली किस्त'
                })
            
            # Pesticide spray
            if days_since_planting > 45:
                activities.append({
                    'activity_type': 'कीटनाशक छिड़काव',
                    'description': 'कीट नियंत्रण',
                    'scheduled_date': crop.planting_date + timedelta(days=45),
                    'status': 'completed',
                    'quantity': '500ml/एकड़',
                    'notes': 'क्लोरपाइरिफॉस 20% EC'
                })
            
            # Weeding
            if days_since_planting > 25:
                activities.append({
                    'activity_type': 'निराई-गुड़ाई',
                    'description': 'खरपतवार नियंत्रण',
                    'scheduled_date': crop.planting_date + timedelta(days=25),
                    'status': 'completed',
                    'quantity': '4 मजदूर',
                    'notes': 'मजदूर: 4 लोग, 1 दिन'
                })
            
            # Today's pending activities
            today_activities = [
                {
                    'activity_type': 'सिंचाई',
                    'description': f'{crop.crop_type} में सिंचाई की आवश्यकता',
                    'scheduled_date': date.today(),
                    'status': 'pending',
                    'quantity': '3 घंटे',
                    'notes': 'मिट्टी सूखी दिख रही है'
                },
                {
                    'activity_type': 'उर्वरक प्रयोग',
                    'description': f'{crop.crop_type} में पोटाश का प्रयोग',
                    'scheduled_date': date.today(),
                    'status': 'pending',
                    'quantity': '30 किग्रा/एकड़',
                    'notes': 'MOP: 30 किग्रा/एकड़'
                }
            ]
            
            # Add some today's activities to select crops
            if crop.status == 'active' and random.choice([True, False]):
                activities.extend(today_activities[:1])  # Add one today activity
            
            # Create activity records
            for activity_data in activities:
                activity = Activity(
                    crop_id=crop.id,
                    **activity_data
                )
                db.session.add(activity)
        
        # Create some disease detection records
        print("Adding disease detection records...")
        
        disease_data = [
            {
                'crop': crops[0],  # Wheat
                'image_path': '/static/test_images/wheat_disease.jpg',
                'predicted_disease': 'पत्ती का धब्बा रोग',
                'confidence_score': 0.855,
                'treatment_suggested': 'प्रोपिकोनाज़ोल का छिड़काव करें। 500ml प्रति एकड़ की दर से।',
                'is_healthy': False,
                'detected_at': datetime.now() - timedelta(days=5)
            },
            {
                'crop': crops[2],  # Potato
                'image_path': '/static/test_images/potato_disease.jpg',
                'predicted_disease': 'आलू का झुलसा रोग',
                'confidence_score': 0.923,
                'treatment_suggested': 'मैंकोजेब का छिड़काव तुरंत करें। दोहराव 10 दिन बाद।',
                'is_healthy': False,
                'detected_at': datetime.now() - timedelta(days=2)
            },
            {
                'crop': crops[5],  # Sugarcane
                'image_path': '/static/test_images/sugarcane_healthy.jpg',
                'predicted_disease': 'स्वस्थ पौधा',
                'confidence_score': 0.782,
                'treatment_suggested': 'कोई उपचार आवश्यक नहीं। संतुलित सिंचाई बनाए रखें।',
                'is_healthy': True,
                'detected_at': datetime.now() - timedelta(days=10)
            }
        ]
        
        for disease_info in disease_data:
            crop = disease_info.pop('crop')
            disease = DiseaseDetection(
                crop_id=crop.id,
                **disease_info
            )
            db.session.add(disease)
        
        db.session.commit()
        
        print(f"\n🎉 Comprehensive test data created successfully!")
        print(f"👤 User: राम किसान (9876543210 / password123)")
        print(f"🏠 Farms: {len(farms)} farms with diverse soil types")
        print(f"🌾 Crops: {len(crops)} crops (active: {len([c for c in crops if c.status == 'active'])})")
        print(f"📋 Activities: Multiple activities with today's pending tasks")
        print(f"🔬 Disease Records: {len(disease_data)} disease detection records")
        print(f"\n📊 Dashboard Features to Explore:")
        print(f"   - Crop distribution charts")
        print(f"   - Monthly activity trends") 
        print(f"   - Weather integration")
        print(f"   - Individual crop analytics")
        print(f"   - Disease management")
        print(f"   - Activity scheduling")
        
        return user

if __name__ == '__main__':
    create_test_user()
