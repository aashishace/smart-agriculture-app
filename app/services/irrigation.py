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
