"""
Smart Irrigation Routes - Enhanced irrigation management system
"""

from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from flask_babel import gettext as _
from app.models.farm import Farm
from app.models.crop import Crop, Activity
from app.services.irrigation import IrrigationService
from app.services.notifications import NotificationService
from app.services.weather import WeatherService
from app import db
from datetime import date, datetime, timedelta
import logging

logger = logging.getLogger(__name__)

irrigation_bp = Blueprint('irrigation', __name__, url_prefix='/irrigation')

@irrigation_bp.route('/')
@login_required
def dashboard():
    """Smart Irrigation Dashboard."""
    # Get basic stats for initial page load
    stats = get_irrigation_stats()
    return render_template('irrigation/dashboard.html', stats=stats)

@irrigation_bp.route('/api/dashboard-stats')
@login_required
def dashboard_stats_api():
    """API endpoint for dashboard statistics."""
    try:
        stats = get_irrigation_stats()
        return jsonify({'success': True, 'stats': stats})
    except Exception as e:
        logger.error(f"Error getting dashboard stats: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@irrigation_bp.route('/api/weather-recommendations')
@login_required
def weather_recommendations_api():
    """API endpoint for weather-based recommendations."""
    try:
        weather_service = WeatherService()
        irrigation_service = IrrigationService()
        
        # Get user's primary farm location for weather data
        primary_farm = current_user.farms.first()
        if not primary_farm:
            return jsonify({
                'success': True,
                'weather': {'temperature': 28, 'humidity': 65, 'rain_probability': 20},
                'recommendation': {
                    'action': 'monitor',
                    'message_hi': 'कोई फार्म नहीं मिला। कृपया पहले फार्म जोड़ें।'
                }
            })
        
        farm_location = primary_farm.get_location()
        
        # Get weather data
        weather_analysis = weather_service.analyze_irrigation_conditions(
            farm_location[0], farm_location[1]
        )
        
        if weather_analysis:
            general_recommendation = generate_general_recommendation(weather_analysis)
            return jsonify({
                'success': True,
                'weather': {
                    'temperature': weather_analysis['current_temperature'],
                    'humidity': weather_analysis['current_humidity'],
                    'rain_probability': weather_analysis['rain_probability_max']
                },
                'recommendation': general_recommendation
            })
        else:
            return jsonify({
                'success': True,
                'weather': {'temperature': 28, 'humidity': 65, 'rain_probability': 20},
                'recommendation': {
                    'action': 'monitor',
                    'message_hi': 'मौसम डेटा उपलब्ध नहीं है। स्थानीय स्थितियों के अनुसार सिंचाई करें।'
                }
            })
            
    except Exception as e:
        logger.error(f"Error getting weather recommendations: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@irrigation_bp.route('/api/schedule')
@login_required
def irrigation_schedule_api():
    """API endpoint for irrigation schedule."""
    try:
        irrigation_service = IrrigationService()
        schedule = []
        
        # Get all user's crops and their irrigation recommendations
        for farm in current_user.farms.all():
            farm_location = farm.get_location()
            for crop in farm.get_active_crops():
                recommendation = irrigation_service.calculate_irrigation_need(crop, farm_location)
                
                # Add crop details to recommendation
                recommendation['crop'] = {
                    'crop_type': crop.crop_type,
                    'variety': crop.variety,
                    'farm_name': farm.farm_name,
                    'area_acres': crop.area_acres
                }
                
                schedule.append(recommendation)
        
        # Sort by priority: urgent > high > medium > low
        priority_order = {'urgent': 0, 'high': 1, 'medium': 2, 'low': 3}
        schedule.sort(key=lambda x: priority_order.get(x['priority'], 4))
        
        return jsonify({'success': True, 'schedule': schedule})
        
    except Exception as e:
        logger.error(f"Error getting irrigation schedule: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@irrigation_bp.route('/api/schedule-all-urgent', methods=['POST'])
@login_required
def schedule_all_urgent_api():
    """API endpoint to schedule irrigation for all urgent crops."""
    try:
        irrigation_service = IrrigationService()
        notification_service = NotificationService()
        scheduled_count = 0
        
        for farm in current_user.farms.all():
            farm_location = farm.get_location()
            for crop in farm.get_active_crops():
                recommendation = irrigation_service.calculate_irrigation_need(crop, farm_location)
                
                if (recommendation['action'] == 'irrigate' and 
                    recommendation['priority'] in ['urgent', 'high']):
                    
                    # Schedule irrigation activity
                    activity = irrigation_service.schedule_irrigation_activity(
                        crop, recommendation['water_amount_mm']
                    )
                    
                    # Send notification
                    notification_service.send_irrigation_alert(
                        current_user.phone,
                        crop.crop_type,
                        f"आज {recommendation['water_amount_mm']}मिमी पानी दें - {recommendation['priority']} प्राथमिकता",
                        current_user.preferred_language
                    )
                    
                    scheduled_count += 1
        
        return jsonify({
            'success': True,
            'scheduled_count': scheduled_count,
            'message': f'{scheduled_count} फसलों के लिए सिंचाई निर्धारित की गई'
        })
        
    except Exception as e:
        logger.error(f"Error bulk scheduling irrigation: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@irrigation_bp.route('/api/refresh-all-recommendations', methods=['POST'])
@login_required
def refresh_all_recommendations_api():
    """API endpoint to refresh all irrigation recommendations."""
    try:
        # This endpoint forces recalculation of all recommendations
        # The actual calculation happens when the schedule is requested
        return jsonify({
            'success': True,
            'message': 'सभी सिफारिशें अपडेट की गईं'
        })
        
    except Exception as e:
        logger.error(f"Error refreshing recommendations: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

def get_irrigation_stats():
    """Get irrigation statistics for dashboard."""
    stats = {
        'total_crops': 0,
        'urgent_irrigation': 0,
        'optimal_status': 0,
        'scheduled_today': 0
    }
    
    try:
        irrigation_service = IrrigationService()
        
        # Count all crops
        total_crops = 0
        urgent_count = 0
        optimal_count = 0
        
        for farm in current_user.farms.all():
            farm_location = farm.get_location()
            active_crops = farm.get_active_crops()
            total_crops += len(active_crops)
            
            for crop in active_crops:
                recommendation = irrigation_service.calculate_irrigation_need(crop, farm_location)
                
                if recommendation['priority'] == 'urgent':
                    urgent_count += 1
                elif recommendation['action'] == 'monitor':
                    optimal_count += 1
        
        # Count scheduled irrigation activities for today
        scheduled_today = Activity.query.join(Crop).join(Farm).filter(
            Farm.user_id == current_user.id,
            Activity.activity_type == 'irrigation',
            Activity.scheduled_date == date.today(),
            Activity.status == 'pending'
        ).count()
        
        stats.update({
            'total_crops': total_crops,
            'urgent_irrigation': urgent_count,
            'optimal_status': optimal_count,
            'scheduled_today': scheduled_today
        })
        
    except Exception as e:
        logger.error(f"Error calculating irrigation stats: {e}")
    
    return stats

def generate_general_recommendation(weather_analysis):
    """Generate general irrigation recommendation based on weather."""
    recommendation = {
        'action': 'monitor',
        'message_hi': 'मौसम की निगरानी करें और आवश्यकतानुसार सिंचाई करें।'
    }
    
    try:
        temp = weather_analysis['current_temperature']
        humidity = weather_analysis['current_humidity']
        rain_prob = weather_analysis['rain_probability_max']
        
        if rain_prob > 70:
            recommendation.update({
                'action': 'skip',
                'message_hi': f'आज सिंचाई न करें - {rain_prob:.0f}% बारिश की संभावना है।'
            })
        elif temp > 35 and humidity < 40:
            recommendation.update({
                'action': 'irrigate',
                'message_hi': f'गर्म और सूखा मौसम ({temp}°C, {humidity}% नमी) - सिंचाई की जरूरत हो सकती है।'
            })
        elif temp < 25 and humidity > 80:
            recommendation.update({
                'action': 'skip',
                'message_hi': f'ठंडा और नम मौसम ({temp}°C, {humidity}% नमी) - सिंचाई की जरूरत कम है।'
            })
        else:
            recommendation.update({
                'action': 'monitor',
                'message_hi': f'मौसम सामान्य है ({temp}°C, {humidity}% नमी) - फसल की स्थिति देखकर सिंचाई करें।'
            })
            
    except Exception as e:
        logger.error(f"Error generating weather recommendation: {e}")
        
    return recommendation
