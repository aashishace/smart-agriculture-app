"""
Main Routes - Dashboard, Home, and General Pages
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from flask_babel import _
from app.models.user import User
from app.models.farm import Farm
from app.models.crop import Crop, Activity, DiseaseDetection
from app import db
from sqlalchemy import func
from app.services.weather import WeatherService
from app.services.irrigation import IrrigationService
from app.services.notifications import NotificationService
from datetime import date, datetime, timedelta, timezone
import logging

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Home page."""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('index.html')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard."""
    # Get user's farms and crops
    farms = current_user.farms.all()
    active_crops = []
    
    for farm in farms:
        active_crops.extend(farm.get_active_crops())
    
    # Get today's activities
    today = date.today()
    today_activities = Activity.query.join(Crop).join(Farm).filter(
        Farm.user_id == current_user.id,
        Activity.scheduled_date == today,
        Activity.status == 'pending'
    ).all()
    
    # Get overdue activities
    overdue_activities = Activity.query.join(Crop).join(Farm).filter(
        Farm.user_id == current_user.id,
        Activity.scheduled_date < today,
        Activity.status == 'pending'
    ).all()
    
    # Get weather for first farm with location
    weather_data = None
    farm_with_location = next((farm for farm in farms if farm.is_location_set()), None)
    
    if farm_with_location:
        weather_service = WeatherService()
        location = farm_with_location.get_location()
        weather_data = weather_service.get_current_weather(location[0], location[1])
    
    # Get irrigation recommendations
    irrigation_service = IrrigationService()
    irrigation_recommendations = []
    
    for farm in farms:
        if farm.is_location_set():
            farm_recommendations = irrigation_service.calculate_farm_irrigation_schedule(farm)
            irrigation_recommendations.extend(farm_recommendations)
    
    # Statistics
    stats = {
        'total_farms': len(farms),
        'active_crops': len(active_crops),
        'pending_activities': len(today_activities),
        'overdue_activities': len(overdue_activities),
        'urgent_irrigation': len([r for r in irrigation_recommendations if r['priority'] == 'urgent']),
        'weather_alerts': 0  # Placeholder for weather alerts
    }
    
    return render_template('dashboard.html', 
                         farms=farms,
                         active_crops=active_crops,
                         pending_activities=today_activities,
                         overdue_activities=overdue_activities,
                         weather_data=weather_data,
                         irrigation_recommendations=irrigation_recommendations,
                         stats=stats,
                         current_date=today.strftime('%d %B %Y'))

@main_bp.route('/api/weather/<float:lat>/<float:lon>')
@login_required
def get_weather_api(lat, lon):
    """API endpoint for weather data."""
    weather_service = WeatherService()
    current_weather = weather_service.get_current_weather(lat, lon)
    forecast = weather_service.get_forecast(lat, lon, days=3)
    
    return jsonify({
        'current': current_weather,
        'forecast': forecast
    })

@main_bp.route('/api/dashboard-stats')
@login_required
def dashboard_stats_api():
    """API endpoint for dashboard statistics."""
    farms = current_user.farms.all()
    
    # Crop distribution
    crop_counts = {}
    for farm in farms:
        for crop in farm.get_active_crops():
            crop_type = crop.crop_type
            crop_counts[crop_type] = crop_counts.get(crop_type, 0) + 1
    
    # Activities by status
    activity_stats = db.session.query(
        Activity.status,
        func.count(Activity.id)
    ).join(Crop).join(Farm).filter(
        Farm.user_id == current_user.id
    ).group_by(Activity.status).all()
    
    activity_counts = {status: count for status, count in activity_stats}
    
    # Recent activity trend (last 7 days)
    activity_trend = []
    for i in range(7):
        day = date.today() - timedelta(days=i)
        day_activities = Activity.query.join(Crop).join(Farm).filter(
            Farm.user_id == current_user.id,
            Activity.completed_date == day
        ).count()
        
        activity_trend.append({
            'date': day.isoformat(),
            'count': day_activities
        })
    
    activity_trend.reverse()  # Show oldest to newest
    
    return jsonify({
        'crop_distribution': crop_counts,
        'activity_status': activity_counts,
        'activity_trend': activity_trend
    })

@main_bp.route('/help')
def help_page():
    """Help and documentation page."""
    return render_template('help.html')

@main_bp.route('/about')
def about():
    """About page."""
    return render_template('about.html')

@main_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    """Contact page."""
    if request.method == 'POST':
        # Handle contact form submission
        name = request.form.get('name', '')
        email = request.form.get('email', '')
        message = request.form.get('message', '')
        
        # In a real app, you'd save this to database or send email
        flash(_('Your message has been sent. We will contact you soon.'), 'success')
        return redirect(url_for('main.contact'))
    
    return render_template('contact.html')

@main_bp.route('/privacy')
def privacy():
    """Privacy policy page."""
    return render_template('privacy.html')

@main_bp.route('/terms')
def terms():
    """Terms of service page."""
    return render_template('terms.html')

@main_bp.route('/onboarding')
@login_required
def onboarding():
    """Onboarding page for new users."""
    # Check if user already has farms
    farms_count = current_user.farms.count()
    
    if farms_count > 0:
        # User already has farms, redirect to dashboard
        return redirect(url_for('main.dashboard'))
    
    return render_template('onboarding.html')

@main_bp.route('/health')
def health_check():
    """Health check endpoint for monitoring."""
    try:
        # Check database connectivity
        db.session.execute(db.text('SELECT 1'))
        
        # Basic health metrics
        health_data = {
            'status': 'healthy',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'database': 'connected',
            'version': '1.0.0'
        }
        
        # Optional: Add more health checks
        try:
            user_count = User.query.count()
            health_data['users'] = user_count
        except Exception:
            pass
            
        return jsonify(health_data), 200
        
    except Exception as e:
        logging.error(f"Health check failed: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'error': 'Database connection failed'
        }), 503

@main_bp.route('/ready')
def readiness_check():
    """Readiness check for Kubernetes/Docker deployments."""
    try:
        # More comprehensive checks for readiness
        db.session.execute(db.text('SELECT 1'))
        
        # Check if essential data exists
        admin_exists = User.query.first() is not None
        
        return jsonify({
            'status': 'ready',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'database': 'ready',
            'data_initialized': admin_exists
        }), 200
        
    except Exception as e:
        logging.error(f"Readiness check failed: {str(e)}")
        return jsonify({
            'status': 'not_ready',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'error': str(e)
        }), 503

# Error handlers
@main_bp.errorhandler(404)
def not_found(error):
    """404 error handler."""
    return render_template('errors/404.html'), 404

@main_bp.errorhandler(500)
def internal_error(error):
    """500 error handler."""
    db.session.rollback()
    return render_template('errors/500.html'), 500
