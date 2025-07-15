"""
Smart Irrigation Service - Calculates irrigation recommendations
"""

from datetime import datetime, date, timedelta
from app.services.weather import WeatherService
from app.models.crop import Crop, Activity
from app import db
import logging

logger = logging.getLogger(__name__)

class IrrigationService:
    """Service for calculating irrigation recommendations."""
    
    def __init__(self):
        self.weather_service = WeatherService()
    
    def calculate_irrigation_need(self, crop, farm_location=None):
        """
        Calculate irrigation recommendation for a specific crop.
        
        Args:
            crop (Crop): The crop object
            farm_location (tuple): (latitude, longitude) of the farm
            
        Returns:
            dict: Irrigation recommendation
        """
        try:
            # Get crop water requirements
            base_water_need = crop.get_water_requirement()
            growth_stage = crop.get_growth_stage_info()
            
            # Get last irrigation activity
            last_irrigation = self._get_last_irrigation(crop)
            days_since_irrigation = self._calculate_days_since_irrigation(last_irrigation)
            
            # Get weather analysis if location available
            weather_analysis = None
            if farm_location:
                weather_analysis = self.weather_service.analyze_irrigation_conditions(
                    farm_location[0], farm_location[1]
                )
            
            # Calculate recommendation
            recommendation = self._calculate_recommendation(
                crop, base_water_need, days_since_irrigation, weather_analysis, growth_stage
            )
            
            return recommendation
            
        except Exception as e:
            logger.error(f"Error calculating irrigation need: {e}")
            return self._get_default_recommendation(crop)
    
    def calculate_farm_irrigation_schedule(self, farm):
        """
        Calculate irrigation schedule for all crops in a farm.
        
        Args:
            farm (Farm): The farm object
            
        Returns:
            list: List of irrigation recommendations for all crops
        """
        recommendations = []
        farm_location = farm.get_location()
        
        for crop in farm.get_active_crops():
            recommendation = self.calculate_irrigation_need(crop, farm_location)
            recommendation['crop'] = crop.to_dict()
            recommendations.append(recommendation)
        
        return recommendations
    
    def schedule_irrigation_activity(self, crop, water_amount_mm, scheduled_date=None):
        """
        Schedule an irrigation activity for a crop.
        
        Args:
            crop (Crop): The crop object
            water_amount_mm (float): Amount of water in mm
            scheduled_date (date): Date to schedule irrigation (default: today)
            
        Returns:
            Activity: Created activity object
        """
        if not scheduled_date:
            scheduled_date = date.today()
        
        activity = Activity(
            crop_id=crop.id,
            activity_type='irrigation',
            description=f'Irrigate {crop.crop_type} with {water_amount_mm}mm water',
            quantity=f'{water_amount_mm}mm',
            scheduled_date=scheduled_date,
            status='pending'
        )
        
        db.session.add(activity)
        db.session.commit()
        
        return activity
    
    def _get_last_irrigation(self, crop):
        """Get the last irrigation activity for a crop."""
        return crop.activities.filter_by(
            activity_type='irrigation',
            status='completed'
        ).order_by(Activity.completed_date.desc()).first()
    
    def _calculate_days_since_irrigation(self, last_irrigation):
        """Calculate days since last irrigation."""
        if last_irrigation and last_irrigation.completed_date:
            return (date.today() - last_irrigation.completed_date).days
        return 7  # Default to 7 days if no irrigation history
    
    def _calculate_recommendation(self, crop, base_water_need, days_since_irrigation, weather_analysis, growth_stage):
        """Calculate detailed irrigation recommendation."""
        
        # Base calculation
        total_water_need = base_water_need * max(1, days_since_irrigation)
        
        # Weather adjustments
        weather_factor = 1.0
        skip_reason = None
        
        if weather_analysis:
            # Skip irrigation if rain expected
            if weather_analysis['rain_probability_max'] > 70:
                skip_reason = "rain_expected"
            elif weather_analysis['rain_next_24h'] > 5:
                skip_reason = "sufficient_rain"
            else:
                # Adjust for temperature and humidity
                if weather_analysis['current_temperature'] > 35:
                    weather_factor *= 1.2
                if weather_analysis['current_humidity'] < 40:
                    weather_factor *= 1.1
                if weather_analysis['wind_speed'] > 15:
                    weather_factor *= 1.15
        
        adjusted_water_need = total_water_need * weather_factor
        
        # Generate recommendation
        if skip_reason:
            action = "skip"
            priority = "low"
            message_en = self._get_skip_message(skip_reason, weather_analysis)
            message_hi = self._get_skip_message_hindi(skip_reason, weather_analysis)
        elif days_since_irrigation >= 2 and adjusted_water_need > 0:
            action = "irrigate"
            priority = self._get_priority(days_since_irrigation, weather_analysis)
            message_en = f"Irrigate with {adjusted_water_need:.1f}mm water"
            message_hi = f"{adjusted_water_need:.1f}मिमी पानी दें"
        else:
            action = "monitor"
            priority = "low"
            message_en = "Monitor crop condition, irrigation not needed today"
            message_hi = "फसल की निगरानी करें, आज सिंचाई की जरूरत नहीं"
        
        return {
            'crop_id': crop.id,
            'action': action,
            'priority': priority,
            'water_amount_mm': round(adjusted_water_need, 1) if action == "irrigate" else 0,
            'days_since_irrigation': days_since_irrigation,
            'growth_stage': growth_stage['stage'],
            'growth_stage_description': growth_stage['description'],
            'message_en': message_en,
            'message_hi': message_hi,
            'weather_factor': round(weather_factor, 2),
            'base_need': base_water_need,
            'weather_analysis': weather_analysis,
            'calculated_at': datetime.now().isoformat()
        }
    
    def _get_priority(self, days_since_irrigation, weather_analysis):
        """Determine irrigation priority."""
        if days_since_irrigation >= 5:
            return "urgent"
        elif days_since_irrigation >= 3:
            return "high"
        elif weather_analysis and weather_analysis['current_temperature'] > 35:
            return "medium"
        else:
            return "low"
    
    def _get_skip_message(self, reason, weather_analysis):
        """Get skip message in English."""
        if reason == "rain_expected":
            prob = weather_analysis['rain_probability_max']
            return f"Skip irrigation - {prob:.0f}% chance of rain expected"
        elif reason == "sufficient_rain":
            rain = weather_analysis['rain_next_24h']
            return f"Skip irrigation - {rain:.1f}mm rain expected in next 24 hours"
        else:
            return "Skip irrigation - weather conditions favorable"
    
    def _get_skip_message_hindi(self, reason, weather_analysis):
        """Get skip message in Hindi."""
        if reason == "rain_expected":
            prob = weather_analysis['rain_probability_max']
            return f"सिंचाई न करें - {prob:.0f}% बारिश की संभावना है"
        elif reason == "sufficient_rain":
            rain = weather_analysis['rain_next_24h']
            return f"सिंचाई न करें - अगले 24 घंटों में {rain:.1f}मिमी बारिश की उम्मीद"
        else:
            return "सिंचाई न करें - मौसम की स्थिति अनुकूल है"
    
    def calculate_optimal_irrigation_time(self, crop, water_amount_mm):
        """Calculate optimal time for irrigation based on weather and efficiency."""
        try:
            # Best irrigation times (hours in 24-hour format)
            optimal_times = [
                {'start': 5, 'end': 8, 'efficiency': 0.95, 'label': 'सुबह जल्दी (5-8 AM)'},
                {'start': 18, 'end': 20, 'efficiency': 0.90, 'label': 'शाम (6-8 PM)'},
                {'start': 20, 'end': 22, 'efficiency': 0.85, 'label': 'रात (8-10 PM)'}
            ]
            
            current_hour = datetime.now().hour
            
            # Find next optimal time
            for time_slot in optimal_times:
                if current_hour < time_slot['start']:
                    return {
                        'recommended_time': time_slot['label'],
                        'efficiency': time_slot['efficiency'],
                        'adjusted_amount': round(water_amount_mm / time_slot['efficiency'], 1),
                        'water_saved': round(water_amount_mm * (1 - time_slot['efficiency']), 1)
                    }
            
            # If past all optimal times today, suggest tomorrow morning
            return {
                'recommended_time': 'कल सुबह (5-8 AM)',
                'efficiency': 0.95,
                'adjusted_amount': round(water_amount_mm / 0.95, 1),
                'water_saved': round(water_amount_mm * 0.05, 1)
            }
            
        except Exception as e:
            logger.error(f"Error calculating optimal irrigation time: {e}")
            return {
                'recommended_time': 'सुबह जल्दी या शाम',
                'efficiency': 0.90,
                'adjusted_amount': water_amount_mm,
                'water_saved': 0
            }
    
    def generate_irrigation_calendar(self, crop, days_ahead=30):
        """Generate irrigation calendar for next 30 days."""
        try:
            calendar = []
            current_date = date.today()
            
            # Get crop water requirements and growth stage progression
            base_water_need = crop.get_water_requirement()
            
            for day in range(days_ahead):
                check_date = current_date + timedelta(days=day)
                
                # Simulate irrigation need (simplified calculation)
                days_since_last = day % 7  # Assume irrigation every 7 days
                
                if days_since_last == 0:  # Irrigation day
                    calendar.append({
                        'date': check_date.isoformat(),
                        'date_formatted': check_date.strftime('%d/%m'),
                        'day_name': self._get_day_name_hindi(check_date.weekday()),
                        'action': 'irrigate',
                        'water_amount': base_water_need,
                        'priority': 'medium',
                        'note': f'{base_water_need}मिमी पानी दें'
                    })
                else:
                    calendar.append({
                        'date': check_date.isoformat(),
                        'date_formatted': check_date.strftime('%d/%m'),
                        'day_name': self._get_day_name_hindi(check_date.weekday()),
                        'action': 'monitor',
                        'water_amount': 0,
                        'priority': 'low',
                        'note': 'फसल की निगरानी करें'
                    })
            
            return calendar
            
        except Exception as e:
            logger.error(f"Error generating irrigation calendar: {e}")
            return []
    
    def _get_day_name_hindi(self, weekday):
        """Get day name in Hindi."""
        days = ['सोमवार', 'मंगलवार', 'बुधवार', 'गुरुवार', 'शुक्रवार', 'शनिवार', 'रविवार']
        return days[weekday]
    
    def calculate_water_efficiency_report(self, farm):
        """Calculate water usage efficiency report for a farm."""
        try:
            # Get all irrigation activities in the last 30 days
            thirty_days_ago = date.today() - timedelta(days=30)
            
            irrigation_activities = Activity.query.join(Crop).filter(
                Crop.farm_id == farm.id,
                Activity.activity_type == 'irrigation',
                Activity.completed_date >= thirty_days_ago,
                Activity.status == 'completed'
            ).all()
            
            total_water_used = 0
            activities_count = len(irrigation_activities)
            
            for activity in irrigation_activities:
                # Extract water amount from quantity field (format: "25.5mm")
                try:
                    water_amount = float(activity.quantity.replace('mm', ''))
                    total_water_used += water_amount
                except:
                    continue
            
            # Calculate efficiency metrics
            farm_area = sum([crop.area_acres for crop in farm.get_active_crops()])
            water_per_acre = total_water_used / max(farm_area, 1)
            
            # Benchmark: 150mm per month is good for most crops
            efficiency_percentage = min(100, (150 / max(water_per_acre, 1)) * 100)
            
            return {
                'total_water_used_mm': round(total_water_used, 1),
                'irrigation_events': activities_count,
                'farm_area_acres': farm_area,
                'water_per_acre': round(water_per_acre, 1),
                'efficiency_percentage': round(efficiency_percentage, 1),
                'efficiency_rating': self._get_efficiency_rating(efficiency_percentage),
                'recommendations': self._get_efficiency_recommendations(efficiency_percentage)
            }
            
        except Exception as e:
            logger.error(f"Error calculating water efficiency: {e}")
            return {
                'total_water_used_mm': 0,
                'irrigation_events': 0,
                'farm_area_acres': 0,
                'water_per_acre': 0,
                'efficiency_percentage': 0,
                'efficiency_rating': 'डेटा उपलब्ध नहीं',
                'recommendations': ['अधिक डेटा संग्रह करें']
            }
    
    def _get_efficiency_rating(self, percentage):
        """Get efficiency rating in Hindi."""
        if percentage >= 90:
            return 'उत्कृष्ट'
        elif percentage >= 75:
            return 'अच्छा'
        elif percentage >= 60:
            return 'औसत'
        else:
            return 'सुधार की जरूरत'
    
    def _get_efficiency_recommendations(self, percentage):
        """Get efficiency improvement recommendations."""
        if percentage >= 90:
            return ['बेहतरीन! वर्तमान तरीके जारी रखें', 'पानी की गुणवत्ता पर ध्यान दें']
        elif percentage >= 75:
            return ['अच्छा प्रदर्शन', 'ड्रिप इरिगेशन का उपयोग करें', 'सिंचाई का समय सुधारें']
        elif percentage >= 60:
            return ['पानी की बचत करें', 'मल्चिंग का उपयोग करें', 'मिट्टी की नमी जांचें']
        else:
            return ['तुरंत सुधार की जरूरत', 'विशेषज्ञ से सलाह लें', 'सिस्टम चेक करें']
    
    def _get_skip_message_hindi(self, reason, weather_analysis):
        """Get skip message in Hindi."""
        if reason == "rain_expected":
            prob = weather_analysis['rain_probability_max']
            return f"सिंचाई न करें - {prob:.0f}% बारिश की संभावना"
        elif reason == "sufficient_rain":
            rain = weather_analysis['rain_next_24h']
            return f"सिंचाई न करें - अगले 24 घंटों में {rain:.1f}मिमी बारिश"
        else:
            return "सिंचाई न करें - मौसम अनुकूल है"
    
    def _get_default_recommendation(self, crop):
        """Get default recommendation when weather data unavailable."""
        growth_stage = crop.get_growth_stage_info()
        base_water_need = crop.get_water_requirement()
        
        return {
            'crop_id': crop.id,
            'action': "irrigate",
            'priority': "medium",
            'water_amount_mm': base_water_need,
            'days_since_irrigation': 0,
            'growth_stage': growth_stage['stage'],
            'growth_stage_description': growth_stage['description'],
            'message_en': f"Irrigate with {base_water_need}mm water (estimated)",
            'message_hi': f"{base_water_need}मिमी पानी दें (अनुमानित)",
            'weather_factor': 1.0,
            'base_need': base_water_need,
            'weather_analysis': None,
            'calculated_at': datetime.now().isoformat()
        }
