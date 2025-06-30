#!/usr/bin/env python3
"""
Add today's activities for better dashboard demonstration
"""

import os
import sys
from datetime import date, datetime, timedelta

# Add the app directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.user import User
from app.models.farm import Farm  
from app.models.crop import Crop, Activity

def add_todays_activities():
    """Add some activities for today to make the dashboard more interesting."""
    
    app = create_app()
    with app.app_context():
        # Find the test user
        user = User.query.filter_by(phone='9876543210').first()
        if not user:
            user = User.query.filter_by(username='ram_kisan').first()
        if not user:
            print("Test user not found. Run create_test_user.py first.")
            print("Available users:")
            for u in User.query.all():
                print(f"  - {u.username} ({u.phone})")
            return
        
        # Get user's active crops
        active_crops = []
        for farm in user.farms:
            active_crops.extend([crop for crop in farm.crops if crop.status == 'active'])
        
        if not active_crops:
            print("No active crops found for the user.")
            return
        
        today = date.today()
        
        # Remove existing today's activities to avoid duplicates
        existing_today_activities = Activity.query.join(Crop).join(Farm).filter(
            Farm.user_id == user.id,
            Activity.scheduled_date == today
        ).all()
        
        for activity in existing_today_activities:
            db.session.delete(activity)
        
        # Create new activities for today
        today_activities = [
            {
                'crop': active_crops[0],  # गेहूं
                'activity_type': 'सिंचाई',
                'description': 'सुबह की सिंचाई - मुख्य खेत',
                'quantity': '2 घंटे',
                'status': 'pending'
            },
            {
                'crop': active_crops[1],  # सरसों
                'activity_type': 'कीटनाशक छिड़काव',
                'description': 'माहू नियंत्रण के लिए छिड़काव',
                'quantity': '50 मिली/एकड़',
                'status': 'pending'
            },
            {
                'crop': active_crops[2] if len(active_crops) > 2 else active_crops[0],  # आलू
                'activity_type': 'निराई-गुड़ाई',
                'description': 'खरपतवार नियंत्रण',
                'quantity': '1 एकड़',
                'status': 'pending'
            },
            {
                'crop': active_crops[0],  # गेहूं
                'activity_type': 'उर्वरक प्रयोग',
                'description': 'यूरिया का प्रयोग - टॉप ड्रेसिंग',
                'quantity': '25 किग्रा/एकड़',
                'status': 'pending'
            }
        ]
        
        for activity_data in today_activities:
            crop = activity_data.pop('crop')
            activity = Activity(
                crop_id=crop.id,
                scheduled_date=today,
                **activity_data
            )
            db.session.add(activity)
        
        db.session.commit()
        print(f"✅ Added {len(today_activities)} activities for today ({today})")
        
        # Also add a few activities for tomorrow
        tomorrow = today + timedelta(days=1)
        tomorrow_activities = [
            {
                'crop': active_crops[0],
                'activity_type': 'खाद डालना',
                'description': 'गुड़ी खाद का प्रयोग',
                'quantity': '500 किग्रा/एकड़',
                'status': 'pending'
            },
            {
                'crop': active_crops[1] if len(active_crops) > 1 else active_crops[0],
                'activity_type': 'सिंचाई',
                'description': 'शाम की सिंचाई',
                'quantity': '1.5 घंटे',
                'status': 'pending'
            }
        ]
        
        for activity_data in tomorrow_activities:
            crop = activity_data.pop('crop')
            activity = Activity(
                crop_id=crop.id,
                scheduled_date=tomorrow,
                **activity_data
            )
            db.session.add(activity)
        
        db.session.commit()
        print(f"✅ Added {len(tomorrow_activities)} activities for tomorrow ({tomorrow})")
        
        print(f"🎯 Dashboard should now show today's tasks!")

if __name__ == '__main__':
    add_todays_activities()
