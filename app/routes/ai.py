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

# Initialize model variables
classifier = None
MODEL_LOADED = False

def initialize_disease_model():
    """Initialize the Hugging Face disease detection model."""
    global classifier, MODEL_LOADED
    
    if MODEL_LOADED and classifier is not None:
        return True
    
    try:
        current_app.logger.info("Loading disease detection model...")
        classifier = pipeline(
            "image-classification", 
            model="linkanjarad/mobilenet_v2_1.0_224-plant-disease-identification"
        )
        MODEL_LOADED = True
        current_app.logger.info("Disease detection model loaded successfully.")
        return True
    except Exception as e:
        current_app.logger.error(f"Failed to load disease detection model: {e}", exc_info=True)
        classifier = None
        MODEL_LOADED = False
        return False


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
    
    # Enhanced file validation
    allowed_extensions = current_app.config.get('ALLOWED_EXTENSIONS', {'png', 'jpg', 'jpeg'})
    if not ('.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in allowed_extensions):
        return jsonify({'error': _('Invalid file type. Use PNG, JPG, or JPEG')}), 400

    # Check file size (16MB limit)
    if file.content_length and file.content_length > current_app.config.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024):
        return jsonify({'error': _('File too large. Maximum size is 16MB')}), 400

    try:
        # Initialize model if not loaded
        if not initialize_disease_model():
            return jsonify({
                'error': _('Disease detection service is currently unavailable. Please try again later.'),
                'model_error': True
            }), 503

        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        upload_dir = current_app.config.get('UPLOAD_FOLDER', 'app/static/uploads')
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, unique_filename)
        file.save(file_path)
        
        # Process image for disease detection
        detection_result = process_disease_detection(file_path)
        
        # Clean up uploaded file
        os.remove(file_path)
        
        # Save to database if crop_id provided
        if crop_id and crop_id.isdigit():
            try:
                import json
                treatment_str = json.dumps(detection_result.get('treatment', {}))
                detection = DiseaseDetection(
                    crop_id=int(crop_id),
                    image_path=unique_filename,
                    predicted_disease=detection_result['disease'],
                    confidence_score=detection_result['confidence'] / 100.0,  # Save as 0-1 scale
                    treatment_suggested=treatment_str,
                    is_healthy=detection_result['is_healthy']
                )
                db.session.add(detection)
                db.session.commit()
                current_app.logger.info(f"Disease detection saved for crop {crop_id}")
            except Exception as db_error:
                current_app.logger.error(f"Failed to save detection to database: {db_error}")
                # Continue anyway - detection still works

        return jsonify({'success': True, 'result': detection_result})
        
    except Exception as e:
        current_app.logger.error(f"Detection failed: {e}", exc_info=True)
        return jsonify({'error': _('Detection failed: %(error)s', error=str(e))}), 500

def process_disease_detection(image_path):
    """
    Processes disease detection using the Hugging Face transformer model.
    Enhanced version with better error handling and confidence interpretation.
    """
    global classifier, MODEL_LOADED
    
    if not MODEL_LOADED or classifier is None:
        return {
            'disease': 'Model Not Available',
            'disease_en': 'Model Not Available',
            'confidence': 0,
            'is_healthy': False,
            'treatment': {
                'immediate_action': 'The AI model is currently unavailable. Please contact support.',
                'organic_treatment': 'Try again later or consult an agricultural expert.',
                'chemical_treatment': 'Service temporarily unavailable.',
                'prevention': 'Manual inspection recommended.'
            },
            'crop_type': 'Unknown',
            'severity': 'unknown',
            'confidence_level': 'unavailable',
            'analysis_details': {
                'error': 'Disease detection model could not be loaded.',
                'model_status': 'unavailable'
            },
            'recommendations': []
        }

    try:
        # Load and preprocess image
        image = Image.open(image_path)
        if image.mode != 'RGB':
            image = image.convert('RGB')

        # Get predictions from model
        predictions = classifier(image)
        
        if not predictions or len(predictions) == 0:
            raise ValueError("No predictions returned from model")
        
        top_prediction = predictions[0]
        
        # Enhanced label parsing with validation
        crop_type, disease_name = parse_model_prediction(top_prediction['label'])
        
        is_healthy = 'healthy' in disease_name.lower()
        confidence_score = float(top_prediction['score'])
        
        # Enhanced confidence thresholds
        HIGH_CONFIDENCE = 0.80
        MEDIUM_CONFIDENCE = 0.60
        LOW_CONFIDENCE = 0.40
        
        # Determine confidence level and reliability
        if confidence_score >= HIGH_CONFIDENCE:
            confidence_level = 'high'
            reliability_message = "High confidence prediction"
        elif confidence_score >= MEDIUM_CONFIDENCE:
            confidence_level = 'medium'
            reliability_message = "Moderate confidence - consider expert consultation"
        elif confidence_score >= LOW_CONFIDENCE:
            confidence_level = 'low'
            reliability_message = "Low confidence - expert diagnosis recommended"
        else:
            confidence_level = 'very_low'
            reliability_message = "Very low confidence - manual inspection required"
            disease_name = "Uncertain Diagnosis"
            crop_type = "Unknown"
        
        # Get treatment information
        treatment_details = get_treatment_details(disease_name, crop_type)
        
        # Enhanced severity assessment
        if is_healthy:
            severity = 'none'
        elif confidence_score > 0.75 and not is_healthy:
            severity = 'high'
        elif confidence_score > 0.60 and not is_healthy:
            severity = 'medium'
        else:
            severity = 'low'

        # Log performance for monitoring
        log_model_performance({
            'confidence': round(confidence_score * 100, 2),
            'confidence_level': confidence_level,
            'disease': disease_name,
            'crop_type': crop_type,
            'is_healthy': is_healthy,
            'analysis_details': {
                'model_version': 'mobilenet_v2_1.0_224'
            }
        }, image_path)

        return {
            'disease': disease_name,
            'disease_en': disease_name,  # For compatibility
            'confidence': round(confidence_score * 100, 2),
            'is_healthy': is_healthy,
            'treatment': treatment_details,
            'crop_type': crop_type,
            'severity': severity,
            'confidence_level': confidence_level,
            'reliability_message': reliability_message,
            'analysis_details': {
                'model_prediction': top_prediction['label'],
                'model_confidence': confidence_score,
                'all_predictions': predictions[:3],  # Top 3 predictions
                'image_processed': True,
                'model_version': 'mobilenet_v2_1.0_224'
            },
            'recommendations': get_prevention_recommendations(crop_type, disease_name)
        }

    except Exception as e:
        current_app.logger.error(f"Error during disease detection: {e}", exc_info=True)
        return {
            'disease': 'Analysis Error',
            'disease_en': 'Analysis Error',
            'confidence': 0.0,
            'is_healthy': False,
            'treatment': {
                'immediate_action': 'An error occurred during analysis. Please try again with a clearer image.',
                'organic_treatment': 'Ensure good lighting and focus on diseased areas.',
                'chemical_treatment': 'Consult local agricultural expert for accurate diagnosis.',
                'prevention': 'Take multiple photos from different angles for better results.'
            },
            'crop_type': 'Unknown',
            'severity': 'unknown',
            'confidence_level': 'error',
            'reliability_message': 'Analysis failed - please try again',
            'analysis_details': {
                'error': str(e),
                'model_status': 'error'
            },
            'recommendations': []
        }

def get_prevention_recommendations(crop_type, disease_name):
    """Get enhanced prevention recommendations for specific crop and disease."""
    recommendations = []
    
    # General prevention recommendations
    recommendations.extend([
        {
            'category': 'General Prevention',
            'recommendation': 'Practice crop rotation every 2-3 seasons',
            'priority': 'high',
            'frequency': 'Seasonal'
        },
        {
            'category': 'General Prevention',
            'recommendation': 'Use certified disease-free seeds and planting material',
            'priority': 'high',
            'frequency': 'Every planting'
        },
        {
            'category': 'Field Hygiene',
            'recommendation': 'Remove crop residues and weeds regularly',
            'priority': 'medium',
            'frequency': 'Weekly'
        }
    ])
    
    # Disease-specific recommendations
    disease_lower = disease_name.lower()
    
    if any(keyword in disease_lower for keyword in ['blight', 'spot', 'rot']):
        recommendations.extend([
            {
                'category': 'Water Management',
                'recommendation': 'Avoid overhead irrigation; use drip or furrow irrigation',
                'priority': 'high',
                'frequency': 'Daily'
            },
            {
                'category': 'Plant Spacing',
                'recommendation': 'Maintain proper plant spacing for air circulation',
                'priority': 'medium',
                'frequency': 'At planting'
            }
        ])
    
    elif any(keyword in disease_lower for keyword in ['rust', 'mildew']):
        recommendations.extend([
            {
                'category': 'Humidity Control',
                'recommendation': 'Water early morning to allow leaves to dry quickly',
                'priority': 'high',
                'frequency': 'Daily'
            },
            {
                'category': 'Preventive Spray',
                'recommendation': 'Apply preventive fungicide spray during humid weather',
                'priority': 'medium',
                'frequency': 'Bi-weekly'
            }
        ])
    
    elif any(keyword in disease_lower for keyword in ['virus', 'mosaic']):
        recommendations.extend([
            {
                'category': 'Vector Control',
                'recommendation': 'Control aphids and whiteflies using yellow sticky traps',
                'priority': 'high',
                'frequency': 'Continuous'
            },
            {
                'category': 'Seed Treatment',
                'recommendation': 'Use virus-tested seeds from certified sources',
                'priority': 'high',
                'frequency': 'Every planting'
            }
        ])
    
    # Crop-specific recommendations
    crop_lower = crop_type.lower()
    
    if crop_lower in ['tomato', 'potato']:
        recommendations.append({
            'category': 'Nutrition',
            'recommendation': 'Avoid excess nitrogen fertilizer which makes plants susceptible',
            'priority': 'medium',
            'frequency': 'Monthly'
        })
    
    elif crop_lower in ['rice', 'wheat']:
        recommendations.append({
            'category': 'Water Management',
            'recommendation': 'Maintain proper water levels - avoid waterlogging',
            'priority': 'high',
            'frequency': 'Daily monitoring'
        })
    
    return recommendations

def parse_model_prediction(label):
    """
    Safely parse model prediction labels with enhanced validation.
    Returns (crop_type, disease_name) tuple.
    """
    try:
        # Handle standard format: "Crop___Disease"
        if '___' in label:
            parts = label.split('___')
            if len(parts) >= 2:
                crop = parts[0].replace('_', ' ').title()
                disease = parts[1].replace('_', ' ').title()
                return crop, disease
        
        # Handle single labels or different formats
        clean_label = label.replace('_', ' ').title()
        
        # Check if it's a healthy plant
        if 'healthy' in clean_label.lower():
            # Try to extract crop name
            words = clean_label.split()
            if len(words) >= 2:
                crop = words[0]
            else:
                crop = 'Plant'
            return crop, 'Healthy'
        
        # For disease labels without clear crop separation
        # Try to identify known crop names at the beginning
        known_crops = [
            'Apple', 'Grape', 'Tomato', 'Potato', 'Corn', 'Maize',
            'Cherry', 'Peach', 'Pepper', 'Orange', 'Strawberry',
            'Soybean', 'Squash', 'Blueberry', 'Raspberry'
        ]
        
        for crop in known_crops:
            if clean_label.lower().startswith(crop.lower()):
                remaining = clean_label[len(crop):].strip()
                return crop, remaining if remaining else 'Unknown Disease'
        
        # Default case
        return 'Unknown Crop', clean_label
        
    except Exception as e:
        current_app.logger.error(f"Error parsing model prediction: {e}")
        return 'Unknown Crop', 'Unknown Disease'

def get_treatment_details(disease_name, crop_type):
    """
    Get detailed treatment information from the database with enhanced fallbacks.
    """
    if 'healthy' in disease_name.lower():
        return {
            'immediate_action': _('No immediate action needed. Your crop looks healthy! 🌱'),
            'organic_treatment': _('Continue with good farming practices and regular monitoring.'),
            'chemical_treatment': _('No chemical treatment required for healthy plants.'),
            'prevention': _('Maintain proper spacing, good air circulation, and balanced nutrition.'),
            'urgency': 'low',
            'estimated_cost': 'No additional cost required',
            'treatment_duration': 'Ongoing maintenance'
        }

    if 'uncertain' in disease_name.lower() or 'unknown' in disease_name.lower():
        return {
            'immediate_action': _('Take additional photos with better lighting and focus on affected areas.'),
            'organic_treatment': _('Monitor plant closely for symptom development.'),
            'chemical_treatment': _('Avoid applying treatments without proper diagnosis.'),
            'prevention': _('Consult local agricultural expert or extension officer for accurate diagnosis.'),
            'urgency': 'medium',
            'estimated_cost': 'Consultation fees may apply',
            'treatment_duration': 'Diagnosis needed first'
        }

    # Try to find specific disease information in database
    disease_info = DiseaseInfo.query.filter(
        db.func.lower(DiseaseInfo.name) == db.func.lower(disease_name)
    ).first()
    
    if disease_info:
        return {
            'immediate_action': disease_info.treatment_immediate or _('Isolate affected plants immediately.'),
            'chemical_treatment': disease_info.treatment_chemical or _('Consult agricultural expert for chemical treatment.'),
            'organic_treatment': disease_info.treatment_organic or _('Improve air circulation and reduce moisture.'),
            'prevention': disease_info.treatment_precautions or _('Practice crop rotation and use disease-resistant varieties.'),
            'urgency': 'high',
            'estimated_cost': 'Varies by treatment method',
            'treatment_duration': '1-4 weeks depending on severity'
        }
    
    # Enhanced fallback treatments based on common disease patterns
    disease_lower = disease_name.lower()
    
    if any(keyword in disease_lower for keyword in ['blight', 'spot', 'rot']):
        return {
            'immediate_action': _('Remove and destroy affected plant parts immediately.'),
            'organic_treatment': _('Apply neem oil spray (2-3ml per liter). Improve drainage and air circulation.'),
            'chemical_treatment': _('Use copper-based fungicide as per manufacturer instructions.'),
            'prevention': _('Avoid overhead watering, ensure good spacing between plants, practice crop rotation.'),
            'urgency': 'high',
            'estimated_cost': '₹200-500 for organic treatment, ₹100-300 for chemical',
            'treatment_duration': '2-3 weeks with regular monitoring'
        }
    
    elif any(keyword in disease_lower for keyword in ['rust', 'mildew', 'fungal']):
        return {
            'immediate_action': _('Reduce humidity around plants and improve air circulation.'),
            'organic_treatment': _('Spray baking soda solution (1 tsp per liter) or milk solution (1:10 ratio).'),
            'chemical_treatment': _('Apply systemic fungicide containing propiconazole or tebuconazole.'),
            'prevention': _('Water at soil level, not on leaves. Ensure morning watering for quick drying.'),
            'urgency': 'medium',
            'estimated_cost': '₹150-400 for treatment',
            'treatment_duration': '1-2 weeks'
        }
    
    elif any(keyword in disease_lower for keyword in ['virus', 'mosaic', 'curl']):
        return {
            'immediate_action': _('Remove infected plants immediately to prevent spread.'),
            'organic_treatment': _('Control insect vectors with neem oil. No direct cure for viral diseases.'),
            'chemical_treatment': _('Use insecticides to control virus-carrying insects (aphids, whiteflies).'),
            'prevention': _('Use virus-free seeds, control insect vectors, maintain field hygiene.'),
            'urgency': 'very_high',
            'estimated_cost': '₹300-600 for vector control',
            'treatment_duration': 'Prevention focused - remove infected plants'
        }
    
    # Generic fallback
    return {
        'immediate_action': _('Isolate affected plants to prevent spread to healthy plants.'),
        'organic_treatment': _('Apply general organic pesticide like neem oil (5ml per liter of water).'),
        'chemical_treatment': _('Consult local agricultural expert for specific chemical treatment recommendations.'),
        'prevention': _('Maintain field hygiene, practice crop rotation, and monitor plants regularly.'),
        'urgency': 'medium',
        'estimated_cost': '₹200-500 for initial treatment',
        'treatment_duration': '2-4 weeks with monitoring'
    }

def log_model_performance(detection_result, image_path):
    """Log model performance for monitoring and improvement."""
    try:
        performance_data = {
            'timestamp': datetime.now().isoformat(),
            'confidence': detection_result.get('confidence', 0),
            'confidence_level': detection_result.get('confidence_level', 'unknown'),
            'disease': detection_result.get('disease', 'unknown'),
            'crop_type': detection_result.get('crop_type', 'unknown'),
            'is_healthy': detection_result.get('is_healthy', False),
            'model_version': detection_result.get('analysis_details', {}).get('model_version', 'unknown'),
            'image_size': os.path.getsize(image_path) if os.path.exists(image_path) else 0,
        }
        
        # Log to application logger
        current_app.logger.info(f"Disease Detection Performance: {performance_data}")
        
        # TODO: In production, send to monitoring service (e.g., Sentry, DataDog)
        # monitor_service.track_prediction(performance_data)
        
    except Exception as e:
        current_app.logger.error(f"Failed to log model performance: {e}")

@ai_bp.route('/model-status')
@login_required
def model_status():
    """Get current model status and health check."""
    global MODEL_LOADED, classifier
    
    status = {
        'model_loaded': MODEL_LOADED,
        'model_available': classifier is not None,
        'timestamp': datetime.now().isoformat(),
        'status': 'healthy' if MODEL_LOADED and classifier else 'unhealthy'
    }
    
    if MODEL_LOADED and classifier:
        try:
            # Test prediction with a small dummy image
            from PIL import Image
            import numpy as np
            
            # Create a simple test image
            test_image = Image.fromarray(np.uint8(np.random.rand(224, 224, 3) * 255))
            test_predictions = classifier(test_image)
            
            status['test_prediction_success'] = True
            status['test_confidence'] = test_predictions[0]['score'] if test_predictions else 0
            
        except Exception as e:
            status['test_prediction_success'] = False
            status['test_error'] = str(e)
            current_app.logger.error(f"Model health check failed: {e}")
    
    return jsonify(status)