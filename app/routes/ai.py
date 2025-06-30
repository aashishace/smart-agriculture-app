"""
AI/ML Routes - Disease Detection and Smart Recommendations
"""

from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, current_app
from flask_login import login_required, current_user
from flask_babel import _
from werkzeug.utils import secure_filename
from app.models.farm import Farm
from app.models.crop import Crop, DiseaseDetection
from app.services.notifications import NotificationService
from app import db
import os
import uuid
from datetime import datetime

ai_bp = Blueprint('ai', __name__)

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
    
    return render_template('ai/disease_scanner.html', crops=all_crops)

@ai_bp.route('/disease-history')
@login_required
def disease_history():
    """Disease detection history."""
    # Get all disease detections for user's crops
    detections = DiseaseDetection.query.join(Crop).join(Farm).filter(
        Farm.user_id == current_user.id
    ).order_by(DiseaseDetection.detected_at.desc()).all()
    
    return render_template('ai/disease_history.html', detections=detections)

@ai_bp.route('/detect-disease', methods=['POST'])
@login_required
def detect_disease():
    """Process disease detection request."""
    
    # Check if file was uploaded
    if 'image' not in request.files:
        return jsonify({'error': _('No image uploaded')}), 400
    
    file = request.files['image']
    crop_id = request.form.get('crop_id')
    
    if file.filename == '':
        return jsonify({'error': _('No file selected')}), 400
    
    if not crop_id or not crop_id.isdigit():
        return jsonify({'error': _('Invalid crop selected')}), 400
    
    # Verify crop belongs to user
    crop = Crop.query.join(Farm).filter(
        Crop.id == int(crop_id),
        Farm.user_id == current_user.id
    ).first()
    
    if not crop:
        return jsonify({'error': _('Crop not found')}), 404
    
    # Validate file type and content
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
    if not ('.' in file.filename and 
            file.filename.rsplit('.', 1)[1].lower() in allowed_extensions):
        return jsonify({'error': _('Invalid file type. Use PNG, JPG, or JPEG')}), 400
    
    # Check file size (already handled by Flask's MAX_CONTENT_LENGTH, but double-check)
    if file.content_length and file.content_length > current_app.config.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024):
        return jsonify({'error': _('File too large. Maximum size is 16MB')}), 400
    
    # Read file content to validate it's actually an image
    file.seek(0)  # Reset file pointer
    file_header = file.read(512)  # Read first 512 bytes
    file.seek(0)  # Reset again for saving
    
    # Basic image file signature validation
    image_signatures = {
        b'\xFF\xD8\xFF': 'jpg',
        b'\x89PNG\r\n\x1a\n': 'png',
        b'GIF87a': 'gif',
        b'GIF89a': 'gif'
    }
    
    is_valid_image = False
    for signature, ext in image_signatures.items():
        if file_header.startswith(signature):
            is_valid_image = True
            break
    
    if not is_valid_image:
        return jsonify({'error': _('Invalid image file. File may be corrupted or not a valid image.')}), 400
    
    try:
        # Save uploaded file
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        
        # Ensure upload directory exists
        upload_dir = current_app.config.get('UPLOAD_FOLDER', 'app/static/uploads')
        os.makedirs(upload_dir, exist_ok=True)
        
        file_path = os.path.join(upload_dir, unique_filename)
        file.save(file_path)
        
        # Process image for disease detection
        detection_result = process_disease_detection(file_path, crop.crop_type)
        
        # Save detection result to database
        detection = DiseaseDetection(
            crop_id=crop.id,
            image_path=unique_filename,
            predicted_disease=detection_result['disease'],
            confidence_score=detection_result['confidence'],
            treatment_suggested=detection_result['treatment'],
            is_healthy=detection_result['is_healthy']
        )
        
        db.session.add(detection)
        db.session.commit()
        
        # Send notification if disease detected with high confidence
        if not detection_result['is_healthy'] and detection_result['confidence'] > 0.8:
            notification_service = NotificationService()
            notification_service.send_disease_alert(
                current_user.phone,
                crop.crop_type,
                detection_result['disease'],
                detection_result['confidence'] * 100,
                detection_result['treatment'],
                current_user.preferred_language
            )
        
        return jsonify({
            'success': True,
            'detection_id': detection.id,
            'result': detection_result
        })
        
    except Exception as e:
        return jsonify({'error': _('Detection failed: %(error)s', error=str(e))}), 500

@ai_bp.route('/api/treatment-advice/<int:detection_id>')
@login_required
def treatment_advice(detection_id):
    """Get detailed treatment advice for a disease detection."""
    detection = DiseaseDetection.query.join(Crop).join(Farm).filter(
        DiseaseDetection.id == detection_id,
        Farm.user_id == current_user.id
    ).first_or_404()
    
    # Get detailed treatment information
    treatment_info = get_treatment_details(detection.predicted_disease, detection.crop.crop_type)
    
    return jsonify({
        'detection': detection.to_dict(),
        'treatment': treatment_info
    })

@ai_bp.route('/api/crop-health-tips/<crop_type>')
@login_required
def crop_health_tips(crop_type):
    """Get general health tips for a crop type."""
    tips = get_crop_health_tips(crop_type)
    return jsonify({'tips': tips})

def process_disease_detection(image_path, crop_type):
    """
    Enhanced disease detection with improved mock algorithm and image analysis.
    In production, this would use a trained CNN model.
    """
    
    # Advanced mock disease detection with image analysis
    import random
    import os
    from PIL import Image
    import numpy as np
    
    try:
        # Basic image analysis for better mock results
        image = Image.open(image_path)
        image_array = np.array(image)
        
        # Simple image features for mock analysis
        brightness = np.mean(image_array)
        variance = np.var(image_array)
        
        # Enhanced disease definitions with severity levels
        diseases = {
            'wheat': [
                {'name': 'Leaf Rust', 'hindi': 'पत्ती की जंग', 'severity': 'medium', 'probability': 0.15},
                {'name': 'Stem Rust', 'hindi': 'तने की जंग', 'severity': 'high', 'probability': 0.10},
                {'name': 'Powdery Mildew', 'hindi': 'चूर्णी फफूंदी', 'severity': 'low', 'probability': 0.20},
                {'name': 'Septoria Leaf Spot', 'hindi': 'सेप्टोरिया पत्ती धब्बा', 'severity': 'medium', 'probability': 0.15},
                {'name': 'Healthy', 'hindi': 'स्वस्थ', 'severity': 'none', 'probability': 0.40}
            ],
            'rice': [
                {'name': 'Brown Spot', 'hindi': 'भूरे धब्बे', 'severity': 'medium', 'probability': 0.20},
                {'name': 'Leaf Blight', 'hindi': 'पत्ती झुलसा', 'severity': 'high', 'probability': 0.15},
                {'name': 'Sheath Blight', 'hindi': 'शीथ ब्लाइट', 'severity': 'high', 'probability': 0.10},
                {'name': 'Rice Blast', 'hindi': 'चावल का धमाका', 'severity': 'high', 'probability': 0.15},
                {'name': 'Healthy', 'hindi': 'स्वस्थ', 'severity': 'none', 'probability': 0.40}
            ],
            'sugarcane': [
                {'name': 'Red Rot', 'hindi': 'लाल सड़न', 'severity': 'high', 'probability': 0.15},
                {'name': 'Smut', 'hindi': 'कंडुआ रोग', 'severity': 'high', 'probability': 0.10},
                {'name': 'Yellow Leaf', 'hindi': 'पीली पत्ती', 'severity': 'medium', 'probability': 0.20},
                {'name': 'Ring Spot', 'hindi': 'रिंग स्पॉट', 'severity': 'low', 'probability': 0.15},
                {'name': 'Healthy', 'hindi': 'स्वस्थ', 'severity': 'none', 'probability': 0.40}
            ],
            'tomato': [
                {'name': 'Early Blight', 'hindi': 'अर्ली ब्लाइट', 'severity': 'medium', 'probability': 0.20},
                {'name': 'Late Blight', 'hindi': 'लेट ब्लाइट', 'severity': 'high', 'probability': 0.15},
                {'name': 'Leaf Mold', 'hindi': 'पत्ती का फफूंद', 'severity': 'medium', 'probability': 0.15},
                {'name': 'Mosaic Virus', 'hindi': 'मोज़ेक वायरस', 'severity': 'high', 'probability': 0.10},
                {'name': 'Healthy', 'hindi': 'स्वस्थ', 'severity': 'none', 'probability': 0.40}
            ],
            'potato': [
                {'name': 'Early Blight', 'hindi': 'अर्ली ब्लाइट', 'severity': 'medium', 'probability': 0.20},
                {'name': 'Late Blight', 'hindi': 'लेट ब्लाइट', 'severity': 'high', 'probability': 0.15},
                {'name': 'Common Scab', 'hindi': 'सामान्य खुजली', 'severity': 'low', 'probability': 0.15},
                {'name': 'Black Scurf', 'hindi': 'काली पपड़ी', 'severity': 'medium', 'probability': 0.10},
                {'name': 'Healthy', 'hindi': 'स्वस्थ', 'severity': 'none', 'probability': 0.40}
            ]
        }
        
        # Get crop-specific diseases or default to wheat
        crop_diseases = diseases.get(crop_type.lower(), diseases['wheat'])
        
        # Weighted random selection based on probabilities
        disease_names = [d['name'] for d in crop_diseases]
        probabilities = [d['probability'] for d in crop_diseases]
        detected_disease_name = np.random.choice(disease_names, p=probabilities)
        
        # Find the selected disease
        detected_disease = next(d for d in crop_diseases if d['name'] == detected_disease_name)
        
        # Calculate confidence based on image quality and disease severity
        base_confidence = random.uniform(0.70, 0.95)
        
        # Adjust confidence based on image brightness (simulating quality)
        if brightness < 50:  # Too dark
            base_confidence *= 0.8
        elif brightness > 200:  # Too bright
            base_confidence *= 0.85
        
        # Adjust confidence based on disease severity
        severity_multipliers = {
            'high': 0.95,
            'medium': 0.88,
            'low': 0.82,
            'none': 0.98
        }
        
        confidence = base_confidence * severity_multipliers.get(detected_disease['severity'], 0.85)
        confidence = min(confidence, 0.98)  # Cap at 98%
        
        is_healthy = detected_disease['name'] == 'Healthy'
        
        # Get comprehensive treatment suggestion
        treatment = get_enhanced_treatment_suggestion(detected_disease['name'], crop_type, detected_disease['severity'])
        
        # Additional analysis results
        analysis_details = {
            'image_quality': 'Good' if 50 <= brightness <= 200 else 'Needs Better Lighting',
            'image_size': f"{image.width}x{image.height}",
            'analysis_time': f"{random.uniform(1.2, 3.5):.1f} seconds",
            'severity_level': detected_disease['severity'].title() if not is_healthy else 'None'
        }
        
        return {
            'disease': detected_disease['hindi'],
            'disease_en': detected_disease['name'],
            'confidence': confidence,
            'is_healthy': is_healthy,
            'treatment': treatment,
            'crop_type': crop_type,
            'severity': detected_disease['severity'],
            'analysis_details': analysis_details,
            'recommendations': get_prevention_recommendations(crop_type, detected_disease['name'])
        }
        
    except Exception as e:
        # Fallback to basic detection
        return {
            'disease': 'विश्लेषण में त्रुटि',
            'disease_en': 'Analysis Error',
            'confidence': 0.0,
            'is_healthy': False,
            'treatment': 'कृषि विशेषज्ञ से संपर्क करें',
            'crop_type': crop_type,
            'severity': 'unknown',
            'analysis_details': {'error': str(e)},
            'recommendations': []
        }

def get_treatment_suggestion(disease_name, crop_type):
    """Get treatment suggestion for detected disease."""
    
    treatments = {
        'Leaf Rust': 'प्रोपिकोनाज़ोल या टेबुकोनाज़ोल स्प्रे करें। 15 दिन बाद दोहराएं।',
        'Stem Rust': 'थायोफैनेट मिथाइल स्प्रे करें। संक्रमित भागों को हटाएं।',
        'Powdery Mildew': 'सल्फर या बाविस्टिन का स्प्रे करें। हवादार रखें।',
        'Brown Spot': 'मैंकोज़ेब या कॉपर ऑक्सीक्लोराइड का स्प्रे करें।',
        'Leaf Blight': 'कार्बेंडाज़िम या प्रोपिकोनाज़ोल का उपयोग करें।',
        'Sheath Blight': 'हेक्साकोनाज़ोल स्प्रे करें। जल भराव से बचें।',
        'Red Rot': 'संक्रमित गन्ने को तुरंत हटाएं। बोरडो मिश्रण का स्प्रे करें।',
        'Smut': 'प्रभावित भागों को जलाएं। कार्बेंडाज़िम से उपचार करें।',
        'Yellow Leaf': 'पोषक तत्वों की कमी। NPK खाद डालें और सिंचाई करें।',
        'Healthy': 'फसल स्वस्थ है। नियमित निगरानी जारी रखें।'
    }
    
    return treatments.get(disease_name, 'कृषि विशेषज्ञ से सलाह लें।')

def get_treatment_details(disease_name, crop_type):
    """Get detailed treatment information."""
    
    # This would contain comprehensive treatment guides
    details = {
        'immediate_action': 'तुरंत उपचार शुरू करें',
        'chemical_treatment': 'रासायनिक उपचार की सूची',
        'organic_treatment': 'जैविक उपचार के विकल्प',
        'prevention': 'भविष्य में बचाव के तरीके',
        'expert_contact': 'विशेषज्ञ से संपर्क की जानकारी'
    }
    
    return details

def get_crop_health_tips(crop_type):
    """Get general health tips for crop."""
    
    tips = {
        'wheat': [
            'नियमित सिंचाई करें लेकिन पानी का भराव न होने दें',
            'बुआई से पहले बीज उपचार जरूर करें',
            'समय पर निराई-गुड़ाई करें',
            'संतुलित खाद का उपयोग करें'
        ],
        'rice': [
            'पानी का स्तर 2-3 सेमी रखें',
            'नर्सरी में स्वस्थ पौधे तैयार करें',
            'समय पर रोपाई करें',
            'जैविक खाद का उपयोग बढ़ाएं'
        ],
        'sugarcane': [
            'गहरी जुताई करें',
            'स्वस्थ बीज गन्ने का चुनाव करें',
            'पर्याप्त अंतराल रखें',
            'मिट्टी में जैविक पदार्थ बढ़ाएं'
        ]
    }
    
    return tips.get(crop_type.lower(), ['नियमित निगरानी करें', 'विशेषज्ञ से सलाह लें'])

def get_enhanced_treatment_suggestion(disease_name, crop_type, severity):
    """Get comprehensive treatment suggestions based on disease and severity."""
    
    treatments = {
        'Leaf Rust': {
            'immediate': 'प्रभावित पत्तियों को तुरंत हटा दें और जला दें',
            'chemical': 'प्रोपिकोनाज़ोल (0.1%) या टेबुकोनाज़ोल (0.1%) का छिड़काव करें',
            'organic': 'नीम का तेल (3%) या बाइकार्बोनेट सोडा (0.5%) का घोल स्प्रे करें',
            'frequency': '15 दिन के अंतराल पर 2-3 बार छिड़काव करें',
            'precautions': 'नम मौसम में छिड़काव न करें, सुबह या शाम को करें'
        },
        'Stem Rust': {
            'immediate': 'संक्रमित तने के हिस्सों को काटकर अलग करें',
            'chemical': 'थायोफैनेट मिथाइल (0.1%) या हेक्साकोनाज़ोल का उपयोग करें',
            'organic': 'तांबे का सल्फेट (0.2%) और चूने का घोल लगाएं',
            'frequency': '10-12 दिन के अंतराल पर उपचार दोहराएं',
            'precautions': 'कटे हुए हिस्सों को तुरंत जला दें या दफना दें'
        },
        'Powdery Mildew': {
            'immediate': 'पौधों के बीच हवा का प्रवाह बढ़ाएं',
            'chemical': 'सल्फर (0.2%) या बाविस्टिन का छिड़काव करें',
            'organic': 'दूध और पानी का घोल (1:10) या बेकिंग सोडा स्प्रे करें',
            'frequency': '7-10 दिन के अंतराल पर छिड़काव करें',
            'precautions': 'अधिक नमी से बचें, ओवरहेड सिंचाई न करें'
        },
        'Brown Spot': {
            'immediate': 'प्रभावित पत्तियों को हटाकर नष्ट करें',
            'chemical': 'मैंकोज़ेब (0.2%) या कॉपर ऑक्सीक्लोराइड का स्प्रे करें',
            'organic': 'त्रिकोडर्मा विरिडी का घोल या नीम का काढ़ा उपयोग करें',
            'frequency': '15 दिन के अंतराल पर 2-3 छिड़काव करें',
            'precautions': 'खेत में पानी का भराव न होने दें'
        },
        'Leaf Blight': {
            'immediate': 'रोगग्रस्त पत्तियों को तुरंत हटा दें',
            'chemical': 'कार्बेंडाज़िम (0.1%) या प्रोपिकोनाज़ोल का छिड़काव करें',
            'organic': 'बॉर्डो मिश्रण (1%) या तांबे का घोल प्रयोग करें',
            'frequency': '10-15 दिन के अंतराल पर उपचार करें',
            'precautions': 'सुबह-शाम के समय छिड़काव करें, धूप में न करें'
        },
        'Sheath Blight': {
            'immediate': 'संक्रमित शीथ को साफ चाकू से काट दें',
            'chemical': 'हेक्साकोनाज़ोल या वैलिडामाइसिन का स्प्रे करें',
            'organic': 'स्यूडोमोनास फ्लोरेसेंस या त्रिकोडर्मा का उपयोग करें',
            'frequency': '12-15 दिन के अंतराल पर 2-3 बार उपचार करें',
            'precautions': 'पानी का स्तर कम रखें, जल निकासी सुनिश्चित करें'
        },
        'Red Rot': {
            'immediate': 'संक्रमित गन्ने को तुरंत काटकर जला दें',
            'chemical': 'कार्बेंडाज़िम (0.1%) या प्रोपिकोनाज़ोल का घोल लगाएं',
            'organic': 'बॉर्डो मिश्रण या त्रिकोडर्मा हार्ज़ियानम का उपयोग करें',
            'frequency': '15-20 दिन के अंतराल पर उपचार दोहराएं',
            'precautions': 'रोगमुक्त बीज गन्ने का ही उपयोग करें'
        },
        'Smut': {
            'immediate': 'कंडुआ रोग से प्रभावित भागों को तुरंत हटाएं',
            'chemical': 'कार्बेंडाज़िम से बीज उपचार और मिट्टी में मिलाएं',
            'organic': 'गर्म पानी से बीज उपचार (50°C पर 2 घंटे)',
            'frequency': 'बुआई से पहले बीज उपचार, फिर मासिक निगरानी',
            'precautions': 'प्रभावित गन्ने को खेत में न छोड़ें, जला दें'
        },
        'Early Blight': {
            'immediate': 'निचली पत्तियों से शुरू होने वाले धब्बों को हटाएं',
            'chemical': 'मैंकोज़ेब (0.2%) या डाइथेन M-45 का छिड़काव करें',
            'organic': 'बेकिंग सोडा (0.5%) या नीम के तेल का स्प्रे करें',
            'frequency': '7-10 दिन के अंतराल पर छिड़काव करें',
            'precautions': 'पत्तियों पर पानी न डालें, ड्रिप सिंचाई करें'
        },
        'Late Blight': {
            'immediate': 'रोगग्रस्त पौधों को तुरंत हटा दें और नष्ट करें',
            'chemical': 'मेटलैक्सिल + मैंकोज़ेब या कॉपर ऑक्सीक्लोराइड स्प्रे करें',
            'organic': 'बॉर्डो मिश्रण (1%) या तांबे का सल्फेट उपयोग करें',
            'frequency': '5-7 दिन के अंतराल पर आवश्यकतानुसार छिड़काव करें',
            'precautions': 'नम मौसम में अधिक सावधानी रखें, पानी का भराव न होने दें'
        }
    }
    
    default_treatment = {
        'immediate': 'प्रभावित भागों को तुरंत हटा दें',
        'chemical': 'कृषि विशेषज्ञ से उपयुक्त दवा की सलाह लें',
        'organic': 'नीम का तेल या जैविक कवकनाशी का प्रयोग करें',
        'frequency': 'विशेषज्ञ की सलाह अनुसार',
        'precautions': 'रोग के लक्षणों पर नज़र रखें'
    }
    
    treatment = treatments.get(disease_name, default_treatment)
    
    # Adjust recommendations based on severity
    if severity == 'high':
        treatment['urgency'] = 'तत्काल उपचार आवश्यक - 24 घंटे के अंदर कार्रवाई करें'
    elif severity == 'medium':
        treatment['urgency'] = 'जल्दी उपचार करें - 2-3 दिन के अंदर'
    elif severity == 'low':
        treatment['urgency'] = 'निगरानी रखें और निवारक उपाय करें'
    else:
        treatment['urgency'] = 'स्वस्थ फसल - नियमित देखभाल जारी रखें'
    
    return treatment

def get_prevention_recommendations(crop_type, disease_name):
    """Get prevention recommendations for specific crop and disease."""
    
    general_prevention = {
        'crop_rotation': 'फसल चक्र अपनाएं - एक ही फसल लगातार न लगाएं',
        'seed_treatment': 'बुआई से पहले बीज उपचार जरूर करें',
        'field_hygiene': 'खेत की सफाई रखें, पुराने अवशेषों को हटाएं',
        'water_management': 'उचित जल प्रबंधन करें, जल भराव से बचें',
        'monitoring': 'नियमित रूप से फसल की निगरानी करें'
    }
    
    disease_specific = {
        'Leaf Rust': [
            'प्रतिरोधी किस्मों का चुनाव करें',
            'नाइट्रोजन की अधिक मात्रा से बचें',
            'पौधों के बीच उचित दूरी रखें'
        ],
        'Powdery Mildew': [
            'हवा का अच्छा प्रवाह सुनिश्चित करें',
            'ओवरहेड सिंचाई से बचें',
            'नम मौसम में विशेष सावधानी रखें'
        ],
        'Brown Spot': [
            'संतुलित पोषण प्रदान करें',
            'पानी का स्तर नियंत्रित रखें',
            'खेत में जैविक पदार्थ बढ़ाएं'
        ],
        'Red Rot': [
            'स्वस्थ और प्रमाणित बीज गन्ने का उपयोग करें',
            'गहरी जुताई करें',
            'जल निकासी का उचित प्रबंध करें'
        ]
    }
    
    recommendations = []
    
    # Add general prevention measures
    for key, value in general_prevention.items():
        recommendations.append({
            'category': 'सामान्य बचाव',
            'recommendation': value,
            'priority': 'medium'
        })
    
    # Add disease-specific recommendations
    if disease_name in disease_specific:
        for rec in disease_specific[disease_name]:
            recommendations.append({
                'category': 'विशिष्ट बचाव',
                'recommendation': rec,
                'priority': 'high'
            })
    
    return recommendations
