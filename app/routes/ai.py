"""
AI/ML Routes - Disease Detection and Smart Recommendations
"""

from flask import Blueprint, render_template, request, jsonify, current_app
from flask_login import login_required, current_user
from flask_babel import _
from werkzeug.utils import secure_filename
from app.models.farm import Farm
from app.models.crop import Crop, DiseaseDetection
from app import db
import os
import uuid
from datetime import datetime
from PIL import Image
from transformers import pipeline
from app.models.crop_data import CropInfo, DiseaseInfo, CropHealthTip

ai_bp = Blueprint('ai', __name__)

# --- Hugging Face Model Integration ---

# Load the pre-trained model pipeline.
try:
    classifier = pipeline("image-classification", model="linkanjarad/mobilenet_v2_1.0_224-plant-disease-identification")
    MODEL_LOADED = True
    # Log model loading success
    # current_app.logger.info("Hugging Face model loaded successfully.")
except Exception as e:
    # If the model fails to load, we'll log the error and disable the feature.
    # current_app.logger.error(f"Failed to load Hugging Face model: {e}", exc_info=True)
    classifier = None
    MODEL_LOADED = False


@ai_bp.route('/disease-scanner')
@login_required
def disease_scanner():
    """Disease detection scanner page."""
    farms = current_user.farms.all()
    all_crops = []
    
    for farm in farms:
        crops = farm.get_active_crops()
        for crop in crops:
            crop_data = crop.to_dict()
            crop_data['farm_name'] = farm.farm_name
            all_crops.append(crop_data)
    
    return render_template('ai/disease_scanner.html', crops=all_crops, model_loaded=MODEL_LOADED)

@ai_bp.route('/disease-history')
@login_required
def disease_history():
    """Disease detection history."""
    detections = DiseaseDetection.query.join(Crop).join(Farm).filter(
        Farm.user_id == current_user.id
    ).order_by(DiseaseDetection.detected_at.desc()).all()
    
    return render_template('ai/disease_history.html', detections=detections)

@ai_bp.route('/detect-disease', methods=['POST'])
@login_required
def detect_disease():
    """Process disease detection request."""
    if 'image' not in request.files:
        return jsonify({'error': _('No image uploaded')}), 400
    
    file = request.files['image']
    crop_id = request.form.get('crop_id')
    
    if file.filename == '':
        return jsonify({'error': _('No file selected')}), 400
    
    # Basic file validation
    allowed_extensions = {'png', 'jpg', 'jpeg'}
    if not ('.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in allowed_extensions):
        return jsonify({'error': _('Invalid file type. Use PNG, JPG, or JPEG')}), 400

    try:
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        upload_dir = current_app.config.get('UPLOAD_FOLDER', 'app/static/uploads')
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, unique_filename)
        file.save(file_path)
        
        # Process image for disease detection using the new model
        detection_result = process_disease_detection(file_path)
        
        os.remove(file_path)
        
        if crop_id and crop_id.isdigit():
            import json
            treatment_str = json.dumps(detection_result.get('treatment', {}))
            detection = DiseaseDetection(
                crop_id=int(crop_id),
                image_path=unique_filename,
                predicted_disease=detection_result['disease'],
                confidence_score=detection_result['confidence'] / 100.0, # Save as 0-1 scale
                treatment_suggested=treatment_str,
                is_healthy=detection_result['is_healthy']
            )
            db.session.add(detection)
            db.session.commit()

        return jsonify({'success': True, 'result': detection_result})
        
    except Exception as e:
        current_app.logger.error(f"Detection failed: {e}", exc_info=True)
        return jsonify({'error': _('Detection failed: %(error)s', error=str(e))}), 500

def process_disease_detection(image_path):
    """
    Processes disease detection using the Hugging Face transformer model.
    """
    if not MODEL_LOADED or classifier is None:
        return {
            'disease': 'Model Not Loaded', 'confidence': 0, 'is_healthy': False,
            'treatment': {'prevention': 'The AI model is currently unavailable. Please contact support.'},
            'crop_type': 'Unknown', 'severity': 'unknown',
            'analysis_details': {'error': 'Model could not be loaded.'}, 'recommendations': []
        }

    try:
        image = Image.open(image_path)
        if image.mode != 'RGB':
            image = image.convert('RGB')

        predictions = classifier(image)
        top_prediction = predictions[0]
        
        # Robustly parse the model's label
        label = top_prediction['label']
        if '___' in label:
            label_parts = label.split('___')
            predicted_crop_type = label_parts[0].replace('_', ' ')
            predicted_disease_name = label_parts[1].replace('_', ' ')
        else:
            # Handle labels without the '___' separator (e.g., "Tomato_healthy")
            predicted_disease_name = label.replace('_', ' ')
            # Attempt to infer crop type from the name, or default to a generic term
            if ' ' in predicted_disease_name:
                 predicted_crop_type = predicted_disease_name.split(' ')[0]
            else:
                 predicted_crop_type = "Plant"
        
        is_healthy = 'healthy' in predicted_disease_name.lower()
        confidence_score = round(top_prediction['score'], 4)
        
        # Confidence Threshold: If confidence is low, classify as uncertain.
        CONFIDENCE_THRESHOLD = 0.90 
        if confidence_score < CONFIDENCE_THRESHOLD and not is_healthy:
            predicted_disease_name = "Uncertain Diagnosis"
            predicted_crop_type = "Unknown"
            is_healthy = False
            treatment_details = get_treatment_details(predicted_disease_name, predicted_crop_type)
        else:
            treatment_details = get_treatment_details(predicted_disease_name, predicted_crop_type)

        return {
            'disease': predicted_disease_name, 'disease_en': predicted_disease_name,
            'confidence': round(confidence_score * 100, 2), 'is_healthy': is_healthy,
            'treatment': treatment_details, 'crop_type': predicted_crop_type,
            'severity': 'high' if confidence_score > 0.8 and not is_healthy else 'medium' if confidence_score > 0.5 and not is_healthy else 'low',
            'analysis_details': {
                'model_prediction': top_prediction['label'],
                'model_confidence': confidence_score,
                'all_predictions': predictions[:3]
            },
            'recommendations': get_prevention_recommendations(predicted_crop_type, predicted_disease_name)
        }

    except Exception as e:
        current_app.logger.error(f"Error during Hugging Face model prediction: {e}", exc_info=True)
        return {
            'disease': 'Analysis Error', 'confidence': 0.0, 'is_healthy': False,
            'treatment': {'prevention': 'An error occurred during analysis. Please try again with a clearer image.'},
            'crop_type': 'Unknown', 'severity': 'unknown',
            'analysis_details': {'error': str(e)}, 'recommendations': []
        }

def get_treatment_details(disease_name, crop_type):
    """
    Get detailed treatment information from the database.
    """
    if 'healthy' in disease_name.lower():
        return {
            'immediate_action': _('No immediate action needed. Your crop looks healthy.'),
            'organic_treatment': _('Continue with good farming practices.'),
            'chemical_treatment': _('No chemical treatment is required.'),
            'prevention': _('Ensure good air circulation and maintain soil health.'),
        }

    disease_info = DiseaseInfo.query.filter(db.func.lower(DiseaseInfo.name) == db.func.lower(disease_name)).first()
    
    if disease_info:
        return {
            'immediate_action': disease_info.treatment_immediate,
            'chemical_treatment': disease_info.treatment_chemical,
            'organic_treatment': disease_info.treatment_organic,
            'prevention': disease_info.treatment_precautions,
        }
    
    return {
        'immediate_action': _('Isolate affected plants to prevent spread.'),
        'organic_treatment': _('Improve air circulation and check soil moisture.'),
        'chemical_treatment': _('No specific treatment found in our database.'),
        'prevention': _('For a definitive diagnosis, consult a local agricultural expert.'),
    }

def get_prevention_recommendations(crop_type, disease_name):
    """Get prevention recommendations for specific crop and disease."""
    return [
        {'category': 'General Prevention', 'recommendation': 'Practice crop rotation.', 'priority': 'medium'},
        {'category': 'General Prevention', 'recommendation': 'Use certified disease-free seeds.', 'priority': 'high'},
    ]