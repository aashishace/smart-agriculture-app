#!/usr/bin/env python3
"""
Create Comprehensive Demo Farmer Account - Sakshi's MCA Project
This script creates a realistic farmer account with complete farming data
for Smart Crop Care Assistant demonstration.
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

def create_comprehensive_demo_farmer():
    """Create a comprehensive demo farmer account for Sakshi's MCA presentation."""
    app = create_app('development')
    
    with app.app_context():
        # Check if demo farmer already exists
        existing_user = User.query.filter_by(phone='8765432109').first()
        if existing_user:
            print("🌾 Demo farmer already exists! Refreshing with latest data...")
            # Delete existing data to recreate with fresh comprehensive data
            for farm in existing_user.farms:
                db.session.delete(farm)
            db.session.commit()
            user = existing_user
        else:
            # Create comprehensive demo farmer account
            user = User(
                name='विकास कुमार शर्मा',  # Vikas Kumar Sharma - Professional farmer name
                phone='8765432109',  # Changed phone number
                email='vikas.farmer@gmail.com',  # Professional email
                village='श्रीनगर',  # Shrinagar village
                state='उत्तर प्रदेश',  # Uttar Pradesh
                preferred_language='hi'  # Hindi preference
            )
            user.set_password('demo2024')  # Updated password
            
            db.session.add(user)
            db.session.commit()
            print(f"✅ Created comprehensive demo farmer: {user.name}")
        
        # Create 4 diverse farms with realistic Indian farming scenarios
        farms_data = [
            {
                'farm_name': 'मुख्य कृषि भूमि',  # Main Agricultural Land
                'area_acres': 12.5,  # Larger main farm
                'soil_type': 'उपजाऊ दोमट',  # Fertile loam
                'latitude': 26.8467,  # Lucknow region coordinates
                'longitude': 80.9462
            },
            {
                'farm_name': 'गंगा तटीय खेत',  # Ganges Riverside Farm
                'area_acres': 8.3,
                'soil_type': 'जलोढ़ मिट्टी',  # Alluvial soil
                'latitude': 26.8500,
                'longitude': 80.9500
            },
            {
                'farm_name': 'पर्वतीय कृषि क्षेत्र',  # Mountain Agricultural Area
                'area_acres': 5.7,
                'soil_type': 'लाल चिकनी मिट्टी',  # Red clay soil
                'latitude': 26.8400,
                'longitude': 80.9400
            },
            {
                'farm_name': 'जैविक खेती केंद्र',  # Organic Farming Center
                'area_acres': 6.2,
                'soil_type': 'काली उर्वर मिट्टी',  # Black fertile soil
                'latitude': 26.8350,
                'longitude': 80.9450
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
        
        # Create diverse crops across farms with realistic Indian farming seasons
        crops_data = [
            # Farm 1 - Main Agricultural Land (मुख्य कृषि भूमि)
            {
                'farm': farms[0],
                'crop_type': 'गेहूं',  # Wheat
                'variety': 'HD-3086 (सकशी किस्म)',  # Including Sakshi variety reference
                'planting_date': date(2024, 11, 20),
                'expected_harvest_date': date(2025, 4, 20),
                'area_acres': 4.5,
                'current_stage': 'tillering',  # Active growth
                'status': 'active'
            },
            {
                'farm': farms[0],
                'crop_type': 'सरसों',  # Mustard
                'variety': 'पूसा मस्टर्ड-27',
                'planting_date': date(2024, 10, 25),
                'expected_harvest_date': date(2025, 3, 25),
                'area_acres': 3.2,
                'current_stage': 'flowering',
                'status': 'active'
            },
            {
                'farm': farms[0],
                'crop_type': 'आलू',  # Potato
                'variety': 'कुफरी सिंदूरी',
                'planting_date': date(2024, 12, 5),
                'expected_harvest_date': date(2025, 3, 20),
                'area_acres': 2.8,
                'current_stage': 'tuber_formation',
                'status': 'active'
            },
            {
                'farm': farms[0],
                'crop_type': 'चना',  # Chickpea
                'variety': 'पूसा चना-256',
                'planting_date': date(2024, 11, 1),
                'expected_harvest_date': date(2025, 4, 1),
                'area_acres': 2.0,
                'current_stage': 'pod_development',
                'status': 'active'
            },
            
            # Farm 2 - Ganges Riverside Farm (गंगा तटीय खेत)
            {
                'farm': farms[1],
                'crop_type': 'चावल',  # Rice
                'variety': 'पूसा बासमती-1',
                'planting_date': date(2024, 6, 20),
                'expected_harvest_date': date(2024, 11, 20),
                'area_acres': 5.0,
                'current_stage': 'harvested',
                'status': 'harvested'
            },
            {
                'farm': farms[1],
                'crop_type': 'मक्का',  # Corn
                'variety': 'गंगा-5 हाइब्रिड',
                'planting_date': date(2024, 7, 5),
                'expected_harvest_date': date(2024, 11, 5),
                'area_acres': 3.3,
                'current_stage': 'harvested',
                'status': 'harvested'
            },
            
            # Farm 3 - Mountain Agricultural Area (पर्वतीय कृषि क्षेत्र)
            {
                'farm': farms[2],
                'crop_type': 'गन्ना',  # Sugarcane
                'variety': 'को-0238 उन्नत',
                'planting_date': date(2024, 3, 15),
                'expected_harvest_date': date(2025, 2, 15),
                'area_acres': 3.5,
                'current_stage': 'maturation',
                'status': 'active'
            },
            {
                'farm': farms[2],
                'crop_type': 'अरहर',  # Pigeon Pea
                'variety': 'ICPL-87119',
                'planting_date': date(2024, 6, 25),
                'expected_harvest_date': date(2025, 1, 25),
                'area_acres': 2.2,
                'current_stage': 'pod_filling',
                'status': 'active'
            },
            
            # Farm 4 - Organic Farming Center (जैविक खेती केंद्र)
            {
                'farm': farms[3],
                'crop_type': 'हल्दी',  # Turmeric
                'variety': 'सुदर्शन हल्दी',
                'planting_date': date(2024, 5, 10),
                'expected_harvest_date': date(2025, 2, 10),
                'area_acres': 2.0,
                'current_stage': 'rhizome_development',
                'status': 'active'
            },
            {
                'farm': farms[3],
                'crop_type': 'धनिया',  # Coriander
                'variety': 'पंत हरितमा',
                'planting_date': date(2024, 11, 10),
                'expected_harvest_date': date(2025, 2, 20),
                'area_acres': 1.8,
                'current_stage': 'vegetative_growth',
                'status': 'active'
            },
            {
                'farm': farms[3],
                'crop_type': 'लहसुन',  # Garlic
                'variety': 'गोदावरी गार्लिक',
                'planting_date': date(2024, 10, 15),
                'expected_harvest_date': date(2025, 4, 15),
                'area_acres': 1.4,
                'current_stage': 'bulb_formation',
                'status': 'active'
            },
            {
                'farm': farms[3],
                'crop_type': 'प्याज',  # Onion
                'variety': 'पूसा रेड',
                'planting_date': date(2024, 12, 1),
                'expected_harvest_date': date(2025, 4, 30),
                'area_acres': 1.0,
                'current_stage': 'bulb_initiation',
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
        
        # Enhanced activity types in Hindi
        activity_types = [
            'बीज बुवाई', 'सिंचाई प्रबंधन', 'जैविक खाद', 'रासायनिक उर्वरक', 
            'कीटनाशक छिड़काव', 'निराई-गुड़ाई', 'रोग प्रबंधन', 'फसल कटाई',
            'मिट्टी परीक्षण', 'बीज उपचार', 'खरपतवार नियंत्रण', 'पानी प्रबंधन'
        ]
        
        # Generate activities for each crop
        for crop in crops:
            # Calculate number of days since planting
            days_since_planting = (date.today() - crop.planting_date).days
            
            # Create activities based on crop stage and time
            activities = []
            
            # Planting activity
            activities.append({
                'activity_type': 'बीज बुवाई',
                'description': f'{crop.crop_type} की उन्नत बुवाई - {crop.variety}',
                'scheduled_date': crop.planting_date,
                'status': 'completed',
                'quantity': '30 किग्रा/एकड़',
                'notes': 'उच्च गुणवत्ता के बीज का प्रयोग'
            })
            
            # Regular irrigation (every 15-20 days)
            irrigation_dates = []
            current_date = crop.planting_date + timedelta(days=10)
            while current_date < date.today() and current_date < crop.expected_harvest_date:
                irrigation_dates.append(current_date)
                current_date += timedelta(days=random.randint(15, 20))
            
            for i, irr_date in enumerate(irrigation_dates):
                activities.append({
                    'activity_type': 'सिंचाई प्रबंधन',
                    'description': f'स्मार्ट सिंचाई #{i+1} - पानी बचत तकनीक',
                    'scheduled_date': irr_date,
                    'status': 'completed' if irr_date <= date.today() else 'pending',
                    'quantity': f'{random.randint(3, 5)} घंटे',
                    'notes': f'ड्रिप इरिगेशन / स्प्रिंकलर सिस्टम'
                })
            
            # Enhanced fertilizer applications
            if days_since_planting > 30:
                activities.append({
                    'activity_type': 'जैविक खाद',
                    'description': 'जैविक खाद और वर्मी कंपोस्ट',
                    'scheduled_date': crop.planting_date + timedelta(days=20),
                    'status': 'completed',
                    'quantity': 'वर्मी कंपोस्ट: 100 किग्रा/एकड़',
                    'notes': 'मिट्टी की उर्वरता बढ़ाने हेतु'
                })
                
                activities.append({
                    'activity_type': 'रासायनिक उर्वरक',
                    'description': 'संतुलित NPK उर्वरक',
                    'scheduled_date': crop.planting_date + timedelta(days=30),
                    'status': 'completed',
                    'quantity': 'यूरिया: 60 किग्रा, DAP: 40 किग्रा',
                    'notes': 'मिट्टी परीक्षण के अनुसार'
                })
            
            # Enhanced pesticide and disease management
            if days_since_planting > 45:
                activities.append({
                    'activity_type': 'कीटनाशक छिड़काव',
                    'description': 'एकीकृत कीट प्रबंधन',
                    'scheduled_date': crop.planting_date + timedelta(days=45),
                    'status': 'completed',
                    'quantity': 'बायो पेस्टिसाइड: 750ml/एकड़',
                    'notes': 'जैविक कीटनाशक का प्रयोग'
                })
            
            # Enhanced weeding
            if days_since_planting > 25:
                activities.append({
                    'activity_type': 'निराई-गुड़ाई',
                    'description': 'यांत्रिक खरपतवार नियंत्रण',
                    'scheduled_date': crop.planting_date + timedelta(days=25),
                    'status': 'completed',
                    'quantity': 'पावर वीडर - 2 घंटे/एकड़',
                    'notes': 'आधुनिक कृषि यंत्र का प्रयोग'
                })
            
            # Enhanced today's activities for Smart Irrigation Dashboard
            today_activities = [
                {
                    'activity_type': 'सिंचाई प्रबंधन',
                    'description': f'{crop.crop_type} में स्मार्ट सिंचाई आवश्यक',
                    'scheduled_date': date.today(),
                    'status': 'pending',
                    'quantity': '4 घंटे - ड्रिप सिस्टम',
                    'notes': 'मौसम आधारित सिंचाई अनुशंसा'
                },
                {
                    'activity_type': 'रासायनिक उर्वरक',
                    'description': f'{crop.crop_type} में पोटेशियम सल्फेट',
                    'scheduled_date': date.today(),
                    'status': 'pending',
                    'quantity': '35 किग्रा/एकड़',
                    'notes': 'फूल और फल विकास हेतु'
                },
                {
                    'activity_type': 'मिट्टी परीक्षण',
                    'description': f'{crop.crop_type} क्षेत्र में pH जांच',
                    'scheduled_date': date.today(),
                    'status': 'pending',
                    'quantity': '5 नमूने प्रति एकड़',
                    'notes': 'मिट्टी की गुणवत्ता मॉनिटरिंग'
                }
            ]
            
            # Add today's activities to active crops randomly
            if crop.status == 'active' and random.choice([True, False]):
                activities.extend(today_activities[:random.randint(1, 2)])  # Add 1-2 today activities
            
            # Create activity records
            for activity_data in activities:
                activity = Activity(
                    crop_id=crop.id,
                    **activity_data
                )
                db.session.add(activity)
        
        # Enhanced disease detection records with more comprehensive data
        print("Adding comprehensive disease detection records...")
        
        disease_data = [
            {
                'crop': crops[0],  # Wheat
                'image_path': '/uploads/diseases/wheat_leaf_rust_2024.jpg',
                'predicted_disease': 'गेहूं का पत्ती रतुआ रोग',
                'confidence_score': 0.892,
                'treatment_suggested': 'प्रोपिकोनाज़ोल 25% EC @ 500ml/एकड़ का छिड़काव करें। 15 दिन बाद दोहराव आवश्यक।',
                'is_healthy': False,
                'detected_at': datetime.now() - timedelta(days=3)
            },
            {
                'crop': crops[2],  # Potato  
                'image_path': '/uploads/diseases/potato_late_blight_2024.jpg',
                'predicted_disease': 'आलू का पिछेता झुलसा रोग',
                'confidence_score': 0.945,
                'treatment_suggested': 'मैंकोजेब 75% WP @ 2.5kg/एकड़ तुरंत छिड़काव। नमी नियंत्रण आवश्यक।',
                'is_healthy': False,
                'detected_at': datetime.now() - timedelta(days=1)
            },
            {
                'crop': crops[6],  # Sugarcane
                'image_path': '/uploads/diseases/sugarcane_healthy_2024.jpg',
                'predicted_disease': 'स्वस्थ गन्ना पौधा',
                'confidence_score': 0.823,
                'treatment_suggested': 'फसल स्वस्थ है। नियमित निगरानी जारी रखें। संतुलित पोषण बनाए रखें।',
                'is_healthy': True,
                'detected_at': datetime.now() - timedelta(days=7)
            },
            {
                'crop': crops[8],  # Turmeric
                'image_path': '/uploads/diseases/turmeric_leaf_spot_2024.jpg',
                'predicted_disease': 'हल्दी का पत्ती धब्बा रोग',
                'confidence_score': 0.767,
                'treatment_suggested': 'कॉपर ऑक्सीक्लोराइड 50% WP @ 3gm/liter पानी में मिलाकर छिड़काव।',
                'is_healthy': False,
                'detected_at': datetime.now() - timedelta(days=12)
            },
            {
                'crop': crops[4],  # Rice (Harvested)
                'image_path': '/uploads/diseases/rice_blast_2024.jpg',
                'predicted_disease': 'धान का ब्लास्ट रोग',
                'confidence_score': 0.856,
                'treatment_suggested': 'ट्राइसाइक्लाज़ोल 75% WP @ 600gm/एकड़ का प्रयोग किया गया।',
                'is_healthy': False,
                'detected_at': datetime.now() - timedelta(days=45)
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
    create_comprehensive_demo_farmer()
