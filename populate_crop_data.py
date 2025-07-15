
"""
Script to populate the database with initial crop and disease data.
"""

import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import db
from app.models.crop_data import CropInfo, GrowthStage, DiseaseInfo

# --- Direct Database Connection ---
DATABASE_URI = 'sqlite:///instance/app.db' 
engine = create_engine(DATABASE_URI)
Session = sessionmaker(bind=engine)
session = Session()

def populate_data():
    """Populate the database with initial data using a direct session."""
    try:
        # Clear existing data
        session.query(DiseaseInfo).delete()
        session.query(GrowthStage).delete
        session.query(CropInfo).delete()
        session.commit()
        
        # Add new data
        add_crop_data()
        
        print("Database populated successfully!")
    except Exception as e:
        print(f"An error occurred: {e}")
        session.rollback()
    finally:
        session.close()

def add_crop_data():
    """Add crop, growth stage, and disease data."""
    
    # Wheat
    wheat = CropInfo(
        name='wheat',
        scientific_name='Triticum aestivum',
        description='A cereal grain, which is a worldwide staple food.',
        avg_harvest_days=140
    )
    session.add(wheat)
    session.commit()
    
    wheat_stages = [
        GrowthStage(crop_info_id=wheat.id, stage_name='germination', stage_description_hi='अंकुरण', start_day=0, end_day=7, water_requirement_mm_day=2),
        # ... (add other stages)
    ]
    session.bulk_save_objects(wheat_stages)
    
    wheat_diseases = [
        DiseaseInfo(crop_info_id=wheat.id, name='Leaf Rust', name_hi='पत्ती की जंग', severity='medium', probability=0.15, treatment_chemical='Propiconazole spray.'),
        DiseaseInfo(crop_info_id=wheat.id, name='Stem Rust', name_hi='तने की जंग', severity='high', probability=0.10, treatment_chemical='Thiophenate methyl spray.'),
        # ... (add other diseases)
    ]
    session.bulk_save_objects(wheat_diseases)
    
    # Rice
    rice = CropInfo(
        name='rice',
        scientific_name='Oryza sativa',
        description='A staple food for a large part of the world\'s human population.',
        avg_harvest_days=150
    )
    session.add(rice)
    session.commit()
    
    # ... (add rice stages and diseases)
    
    session.commit()

if __name__ == '__main__':
    # Bind the engine to the metadata of the Base class so that the
    # declaratives can be accessed through a DBSession instance
    db.Model.metadata.create_all(engine)
    populate_data()
