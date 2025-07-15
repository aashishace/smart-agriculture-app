import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models.crop_data import CropHealthTip

def populate_tips():
    """Populates the crop_health_tips table with initial data."""
    app = create_app('development')
    with app.app_context():
        tips_data = {
            'wheat': [
                ('General', 'नियमित सिंचाई करें लेकिन पानी का भराव न होने दें', 'Regularly irrigate but avoid waterlogging.'),
                ('Seed Treatment', 'बुआई से पहले बीज उपचार जरूर करें', 'Always treat seeds before sowing.'),
                ('Weed Control', 'समय पर निराई-गुड़ाई करें', 'Perform weeding and hoeing on time.'),
                ('Fertilization', 'संतुलित खाद का उपयोग कर���ं', 'Use a balanced fertilizer.')
            ],
            'rice': [
                ('Irrigation', 'पानी का स्तर 2-3 सेमी रखें', 'Maintain a water level of 2-3 cm.'),
                ('Nursery', 'नर्सरी में स्वस्थ पौधे तैयार करें', 'Prepare healthy seedlings in the nursery.'),
                ('Planting', 'समय पर रोपाई करें', 'Transplant on time.'),
                ('Fertilization', 'जैविक खाद का उपयोग बढ़ाएं', 'Increase the use of organic manure.')
            ],
            'sugarcane': [
                ('Tillage', 'गहरी जुताई करें', 'Perform deep ploughing.'),
                ('Seed Selection', 'स्वस्थ बीज गन्ने का चुनाव करें', 'Select healthy seed canes.'),
                ('Spacing', 'पर्याप्त अंतराल रखें', 'Maintain adequate spacing.'),
                ('Soil Health', 'मिट्टी में जैविक पदार्थ बढ़ाएं', 'Increase organic matter in the soil.')
            ]
        }

        for crop_name, tips in tips_data.items():
            for category, tip_hi, tip_en in tips:
                # Check if the tip already exists
                existing_tip = CropHealthTip.query.filter_by(
                    crop_name=crop_name,
                    tip_category=category,
                    tip_en=tip_en
                ).first()
                if not existing_tip:
                    new_tip = CropHealthTip(
                        crop_name=crop_name,
                        tip_category=category,
                        tip_hi=tip_hi,
                        tip_en=tip_en
                    )
                    db.session.add(new_tip)

        db.session.commit()
        print("Crop health tips have been populated.")

if __name__ == '__main__':
    populate_tips()
