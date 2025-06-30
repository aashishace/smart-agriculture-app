"""
Activity Template Service - Pre-defined activity templates for different crops
"""

from datetime import date, timedelta
from app.models.crop import Activity
from app import db

class ActivityTemplateService:
    """Service for managing activity templates and smart scheduling."""
    
    def __init__(self):
        self.activity_templates = self._load_activity_templates()
    
    def _load_activity_templates(self):
        """Load pre-defined activity templates for different crops."""
        return {
            'wheat': [
                {
                    'stage': 'germination',
                    'days_after_planting': 3,
                    'activity_type': 'irrigation',
                    'description': 'First irrigation after germination',
                    'description_hi': 'अंकुरण के बाद पहली सिंचाई',
                    'quantity': '25mm',
                    'priority': 'high'
                },
                {
                    'stage': 'germination',
                    'days_after_planting': 7,
                    'activity_type': 'fertilizer',
                    'description': 'Apply starter fertilizer (DAP)',
                    'description_hi': 'शुरुआती खाद (DAP) डालें',
                    'quantity': '50kg/acre',
                    'priority': 'medium'
                },
                {
                    'stage': 'tillering',
                    'days_after_planting': 25,
                    'activity_type': 'irrigation',
                    'description': 'Tillering stage irrigation',
                    'description_hi': 'कल्ले निकलने के समय सिंचाई',
                    'quantity': '35mm',
                    'priority': 'high'
                },
                {
                    'stage': 'tillering',
                    'days_after_planting': 30,
                    'activity_type': 'fertilizer',
                    'description': 'Apply nitrogen fertilizer (Urea)',
                    'description_hi': 'नाइट्रोजन खाद (यूरिया) डालें',
                    'quantity': '65kg/acre',
                    'priority': 'high'
                },
                {
                    'stage': 'jointing',
                    'days_after_planting': 55,
                    'activity_type': 'irrigation',
                    'description': 'Jointing stage irrigation',
                    'description_hi': 'गांठ बनने के समय सिंचाई',
                    'quantity': '40mm',
                    'priority': 'high'
                },
                {
                    'stage': 'flowering',
                    'days_after_planting': 85,
                    'activity_type': 'irrigation',
                    'description': 'Critical flowering stage irrigation',
                    'description_hi': 'फूल आने के समय अति महत्वपूर्ण सिंचाई',
                    'quantity': '45mm',
                    'priority': 'urgent'
                },
                {
                    'stage': 'grain_filling',
                    'days_after_planting': 105,
                    'activity_type': 'irrigation',
                    'description': 'Grain filling irrigation',
                    'description_hi': 'दाना भरने के समय सिंचाई',
                    'quantity': '35mm',
                    'priority': 'high'
                }
            ],
            'rice': [
                {
                    'stage': 'transplanting',
                    'days_after_planting': 1,
                    'activity_type': 'irrigation',
                    'description': 'Initial flooding after transplanting',
                    'description_hi': 'रोपाई के बाद प्रारंभिक जल भराव',
                    'quantity': '50mm',
                    'priority': 'urgent'
                },
                {
                    'stage': 'vegetative',
                    'days_after_planting': 15,
                    'activity_type': 'fertilizer',
                    'description': 'Apply nitrogen fertilizer',
                    'description_hi': 'नाइट्रोजन खाद डालें',
                    'quantity': '40kg/acre',
                    'priority': 'high'
                },
                {
                    'stage': 'tillering',
                    'days_after_planting': 35,
                    'activity_type': 'irrigation',
                    'description': 'Maintain water level during tillering',
                    'description_hi': 'कल्ले निकलने के समय पानी का स्तर बनाए रखें',
                    'quantity': '2-3cm depth',
                    'priority': 'high'
                },
                {
                    'stage': 'flowering',
                    'days_after_planting': 75,
                    'activity_type': 'irrigation',
                    'description': 'Critical flowering irrigation',
                    'description_hi': 'फूल आने के समय अति महत्वपूर्ण सिंचाई',
                    'quantity': '5cm depth',
                    'priority': 'urgent'
                }
            ],
            'sugarcane': [
                {
                    'stage': 'germination',
                    'days_after_planting': 10,
                    'activity_type': 'irrigation',
                    'description': 'Post-planting irrigation',
                    'description_hi': 'रोपाई के बाद सिंचाई',
                    'quantity': '60mm',
                    'priority': 'high'
                },
                {
                    'stage': 'tillering',
                    'days_after_planting': 45,
                    'activity_type': 'fertilizer',
                    'description': 'Apply NPK fertilizer',
                    'description_hi': 'NPK खाद डालें',
                    'quantity': '120kg/acre',
                    'priority': 'high'
                },
                {
                    'stage': 'grand_growth',
                    'days_after_planting': 120,
                    'activity_type': 'irrigation',
                    'description': 'Growth phase irrigation',
                    'description_hi': 'विकास अवस्था में सिंचाई',
                    'quantity': '80mm',
                    'priority': 'high'
                }
            ]
        }
    
    def get_crop_templates(self, crop_type):
        """Get activity templates for a specific crop type."""
        return self.activity_templates.get(crop_type.lower(), [])
    
    def get_crop_activity_templates(self, crop_type):
        """Get activity templates for crops - alias for get_crop_templates."""
        return self.get_crop_templates(crop_type)
    
    def get_activity_templates_for_stage(self, crop_type, stage):
        """Get activities for specific growth stage."""
        templates = self.get_crop_templates(crop_type)
        return [t for t in templates if t['stage'] == stage]
    
    def generate_activities_for_crop(self, crop):
        """Generate activity schedule for a crop based on templates."""
        templates = self.get_crop_templates(crop.crop_type.lower())
        activities = []
        
        for template in templates:
            activity_date = crop.planting_date + timedelta(days=template['days_after_planting'])
            
            # Only create activities for future dates
            if activity_date >= date.today():
                activity = Activity(
                    crop_id=crop.id,
                    activity_type=template['activity_type'],
                    description=template.get('description_hi', template['description']),
                    scheduled_date=activity_date,
                    quantity=template.get('quantity', ''),
                    status='pending'
                )
                activities.append(activity)
        
        return activities
    
    def create_bulk_activities(self, activities):
        """Create multiple activities in bulk."""
        try:
            for activity in activities:
                db.session.add(activity)
            db.session.commit()
            return {'success': True, 'count': len(activities)}
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': str(e)}
    
    def generate_crop_schedule(self, crop, language='hi'):
        """Generate a complete activity schedule for a crop based on templates."""
        crop_type = crop.crop_type.lower()
        templates = self.get_crop_templates(crop_type)
        
        activities = []
        for template in templates:
            scheduled_date = crop.planting_date + timedelta(days=template['days_after_planting'])
            
            # Only schedule future activities or activities within 3 days past
            if scheduled_date >= date.today() - timedelta(days=3):
                activity_data = {
                    'crop_id': crop.id,
                    'activity_type': template['activity_type'],
                    'description': template['description_hi'] if language == 'hi' else template['description'],
                    'quantity': template['quantity'],
                    'scheduled_date': scheduled_date,
                    'status': 'pending',
                    'priority': template.get('priority', 'medium'),
                    'stage': template['stage']
                }
                activities.append(activity_data)
        
        return activities
    
    def create_activities_from_template(self, crop, language='hi'):
        """Create actual Activity objects from templates for a crop."""
        activities_data = self.generate_crop_schedule(crop, language)
        created_activities = []
        
        for activity_data in activities_data:
            # Check if similar activity already exists
            existing = Activity.query.filter_by(
                crop_id=crop.id,
                activity_type=activity_data['activity_type'],
                scheduled_date=activity_data['scheduled_date']
            ).first()
            
            if not existing:
                activity = Activity(**activity_data)
                db.session.add(activity)
                created_activities.append(activity)
        
        if created_activities:
            db.session.commit()
        
        return created_activities
    
    def get_suggested_activities(self, crop):
        """Get activity suggestions based on crop stage and weather."""
        stage_info = crop.get_growth_stage_info()
        current_stage = stage_info['stage']
        days_planted = crop.get_days_since_planting()
        
        templates = self.get_crop_templates(crop.crop_type)
        suggestions = []
        
        for template in templates:
            # Suggest activities for current stage or upcoming stage
            if (template['stage'] == current_stage or 
                abs(template['days_after_planting'] - days_planted) <= 7):
                
                suggestions.append({
                    'template': template,
                    'suggested_date': crop.planting_date + timedelta(days=template['days_after_planting']),
                    'urgency': self._calculate_urgency(template, days_planted)
                })
        
        # Sort by urgency
        suggestions.sort(key=lambda x: x['urgency'], reverse=True)
        return suggestions[:5]  # Return top 5 suggestions
    
    def _calculate_urgency(self, template, days_planted):
        """Calculate urgency score for an activity suggestion."""
        days_difference = abs(template['days_after_planting'] - days_planted)
        priority_score = {'urgent': 10, 'high': 7, 'medium': 5, 'low': 3}.get(template.get('priority', 'medium'), 5)
        
        # Higher urgency for activities that are due now
        if days_difference <= 2:
            return priority_score + 5
        elif days_difference <= 5:
            return priority_score + 2
        else:
            return priority_score
    
    def get_activity_types(self):
        """Get list of all available activity types."""
        return [
            {'value': 'irrigation', 'label_hi': 'सिंचाई', 'label_en': 'Irrigation'},
            {'value': 'fertilizer', 'label_hi': 'खाद', 'label_en': 'Fertilizer'},
            {'value': 'pesticide', 'label_hi': 'कीटनाशक', 'label_en': 'Pesticide'},
            {'value': 'weeding', 'label_hi': 'निराई', 'label_en': 'Weeding'},
            {'value': 'harvesting', 'label_hi': 'कटाई', 'label_en': 'Harvesting'},
            {'value': 'soil_preparation', 'label_hi': 'मिट्टी तैयारी', 'label_en': 'Soil Preparation'},
            {'value': 'other', 'label_hi': 'अन्य', 'label_en': 'Other'}
        ]
