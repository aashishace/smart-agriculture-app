"""
API Routes for Data Visualization
Provides data endpoints for charts and graphs
"""

from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app.models.user import User
from app.models.farm import Farm
from app.models.crop import Crop, Activity, DiseaseDetection
from app import db
from sqlalchemy import func, desc
from datetime import datetime, timedelta, date
import calendar

api_bp = Blueprint('api', __name__)

@api_bp.route('/test')
def test_endpoint():
    """Test endpoint to verify API blueprint is working."""
    return jsonify({
        'status': 'success',
        'message': 'API blueprint is working correctly',
        'timestamp': datetime.now().isoformat()
    })

@api_bp.route('/charts/crop-growth/<int:crop_id>')
@login_required
def crop_growth_data(crop_id):
    """Get crop growth data for timeline chart."""
    crop = Crop.query.join(Farm).filter(
        Crop.id == crop_id,
        Farm.user_id == current_user.id
    ).first_or_404()
    
    # Calculate growth stages based on days since planting
    stages = []
    if crop.planting_date:
        growth_stages = {
            'wheat': [
                {'name': 'अंकुरण', 'days': 7, 'color': '#10B981'},
                {'name': 'कल्ले निकलना', 'days': 40, 'color': '#059669'},
                {'name': 'जोड़ बनना', 'days': 70, 'color': '#047857'},
                {'name': 'फूल आना', 'days': 100, 'color': '#065F46'},
                {'name': 'दाना भरना', 'days': 130, 'color': '#064E3B'},
                {'name': 'पकना', 'days': 140, 'color': '#FCD34D'}
            ],
            'rice': [
                {'name': 'अंकुरण', 'days': 10, 'color': '#10B981'},
                {'name': 'कल्ले निकलना', 'days': 45, 'color': '#059669'},
                {'name': 'फूल आना', 'days': 90, 'color': '#047857'},
                {'name': 'दूध की अवस्था', 'days': 120, 'color': '#065F46'},
                {'name': 'पकना', 'days': 150, 'color': '#FCD34D'}
            ],
            'sugarcane': [
                {'name': 'अंकुरण', 'days': 30, 'color': '#10B981'},
                {'name': 'कल्ले निकलना', 'days': 90, 'color': '#059669'},
                {'name': 'तेज वृद्धि', 'days': 240, 'color': '#047857'},
                {'name': 'पकना', 'days': 365, 'color': '#FCD34D'}
            ]
        }
        
        crop_stages = growth_stages.get(crop.crop_type.lower(), growth_stages['wheat'])
        days_planted = (date.today() - crop.planting_date).days
        
        for i, stage in enumerate(crop_stages):
            is_current = (i == 0 or days_planted >= crop_stages[i-1]['days']) and days_planted < stage['days']
            is_completed = days_planted >= stage['days']
            
            stages.append({
                'name': stage['name'],
                'days': stage['days'],
                'color': stage['color'],
                'current': is_current,
                'completed': is_completed,
                'progress': min(100, (days_planted / stage['days']) * 100) if is_current else (100 if is_completed else 0)
            })
    
    return jsonify({
        'crop_name': f"{crop.crop_type.title()} ({crop.variety or 'सामान्य'})",
        'planting_date': crop.planting_date.isoformat() if crop.planting_date else None,
        'days_planted': (date.today() - crop.planting_date).days if crop.planting_date else 0,
        'stages': stages
    })

@api_bp.route('/charts/activity-timeline/<int:crop_id>')
@login_required
def activity_timeline_data(crop_id):
    """Get activity timeline data for the crop."""
    crop = Crop.query.join(Farm).filter(
        Crop.id == crop_id,
        Farm.user_id == current_user.id
    ).first_or_404()
    
    # Get activities for the past 3 months
    three_months_ago = date.today() - timedelta(days=90)
    activities = Activity.query.filter(
        Activity.crop_id == crop_id,
        Activity.scheduled_date >= three_months_ago
    ).order_by(Activity.scheduled_date).all()
    
    # Group activities by type
    activity_data = {}
    activity_colors = {
        'irrigation': '#3B82F6',
        'fertilizer': '#10B981', 
        'pesticide': '#F59E0B',
        'harvesting': '#EF4444',
        'other': '#6B7280'
    }
    
    for activity in activities:
        activity_type = activity.activity_type
        if activity_type not in activity_data:
            activity_data[activity_type] = {
                'label': activity_type.title(),
                'data': [],
                'backgroundColor': activity_colors.get(activity_type, '#6B7280'),
                'borderColor': activity_colors.get(activity_type, '#6B7280')
            }
        
        activity_data[activity_type]['data'].append({
            'x': activity.scheduled_date.isoformat(),
            'y': activity_type,
            'description': activity.description or f"{activity_type.title()} गतिविधि",
            'status': activity.status,
            'quantity': activity.quantity
        })
    
    return jsonify({
        'crop_name': f"{crop.crop_type.title()}",
        'datasets': list(activity_data.values())
    })

@api_bp.route('/charts/weather-trends')
@login_required
def weather_trends_data():
    """Get weather trends data (mock data for now)."""
    # Generate mock weather data for the past 7 days
    end_date = date.today()
    start_date = end_date - timedelta(days=6)  # 7 days total (including today)
    
    weather_data = []
    temperatures = []
    humidity = []
    rainfall = []
    labels = []
    
    current_date = start_date
    while current_date <= end_date:
        # Mock weather data - more realistic for Indian summer
        import random
        # Summer temperatures in northern India (June)
        temp = random.randint(35, 45)  # Higher temperatures
        hum = random.randint(45, 75)   # Moderate to high humidity
        rain = random.randint(0, 15) if random.random() > 0.8 else 0  # Occasional rain
        
        labels.append(current_date.strftime('%d %b'))
        temperatures.append(temp)
        humidity.append(hum)
        rainfall.append(rain)
        
        current_date += timedelta(days=1)
    
    return jsonify({
        'labels': labels,
        'datasets': [
            {
                'label': 'तापमान (°C)',
                'data': temperatures,
                'borderColor': '#EF4444',
                'backgroundColor': '#FEF2F2',
                'yAxisID': 'y'
            },
            {
                'label': 'नमी (%)',
                'data': humidity,
                'borderColor': '#3B82F6',
                'backgroundColor': '#EFF6FF',
                'yAxisID': 'y'
            },
            {
                'label': 'बारिश (mm)',
                'data': rainfall,
                'borderColor': '#10B981',
                'backgroundColor': '#F0FDF4',
                'type': 'bar',
                'yAxisID': 'y1'
            }
        ]
    })

@api_bp.route('/charts/yield-prediction/<int:crop_id>')
@login_required
def yield_prediction_data(crop_id):
    """Get yield prediction data for the crop."""
    crop = Crop.query.join(Farm).filter(
        Crop.id == crop_id,
        Farm.user_id == current_user.id
    ).first_or_404()
    
    # Mock yield prediction based on crop type and area
    yield_per_acre = {
        'wheat': {'min': 20, 'avg': 25, 'max': 30},
        'rice': {'min': 30, 'avg': 35, 'max': 40},
        'sugarcane': {'min': 400, 'avg': 500, 'max': 600},
        'corn': {'min': 25, 'avg': 30, 'max': 35},
        'cotton': {'min': 15, 'avg': 20, 'max': 25}
    }
    
    crop_yield = yield_per_acre.get(crop.crop_type.lower(), yield_per_acre['wheat'])
    area = float(crop.area_acres)
    
    # Calculate predictions
    predictions = {
        'pessimistic': crop_yield['min'] * area,
        'realistic': crop_yield['avg'] * area,
        'optimistic': crop_yield['max'] * area
    }
    
    # Mock monthly yield development
    if crop.planting_date:
        days_planted = (date.today() - crop.planting_date).days
        growth_progress = min(100, (days_planted / 140) * 100)  # Assuming 140 days cycle
    else:
        growth_progress = 50
    
    monthly_data = []
    current_yield = 0
    for month in range(6):  # 6 months projection
        progress = min(100, growth_progress + (month * 16.67))  # 100/6 = 16.67
        current_yield = (predictions['realistic'] * progress) / 100
        monthly_data.append(round(current_yield, 1))
    
    return jsonify({
        'crop_name': f"{crop.crop_type.title()}",
        'area_acres': area,
        'unit': 'क्विंटल' if crop.crop_type.lower() != 'sugarcane' else 'टन',
        'predictions': predictions,
        'monthly_projection': {
            'labels': ['महीना 1', 'महीना 2', 'महीना 3', 'महीना 4', 'महीना 5', 'महीना 6'],
            'data': monthly_data
        },
        'current_progress': round(growth_progress, 1)
    })

@api_bp.route('/charts/dashboard-overview')
@login_required
def dashboard_overview_data():
    """Get dashboard overview charts data."""
    # Crop distribution by type
    crop_distribution = db.session.query(
        Crop.crop_type,
        func.count(Crop.id).label('count'),
        func.sum(Crop.area_acres).label('total_area')
    ).join(Farm).filter(
        Farm.user_id == current_user.id,
        Crop.status == 'active'
    ).group_by(Crop.crop_type).all()
    
    crop_labels = []
    crop_counts = []
    crop_areas = []
    crop_colors = ['#EF4444', '#10B981', '#3B82F6', '#F59E0B', '#8B5CF6', '#EC4899']
    
    for i, (crop_type, count, area) in enumerate(crop_distribution):
        crop_labels.append(crop_type.title())
        crop_counts.append(count)
        crop_areas.append(float(area or 0))
    
    # Monthly activity trends
    six_months_ago = date.today() - timedelta(days=180)
    monthly_activities = db.session.query(
        func.strftime('%Y-%m', Activity.scheduled_date).label('month'),
        Activity.activity_type,
        func.count(Activity.id).label('count')
    ).join(Crop).join(Farm).filter(
        Farm.user_id == current_user.id,
        Activity.scheduled_date >= six_months_ago
    ).group_by('month', Activity.activity_type).all()
    
    # Process monthly data
    months = {}
    activity_types = set()
    
    for month, activity_type, count in monthly_activities:
        if month not in months:
            months[month] = {}
        months[month][activity_type] = count
        activity_types.add(activity_type)
    
    # Prepare monthly chart data
    sorted_months = sorted(months.keys())
    month_labels = []
    for month in sorted_months:
        try:
            year, month_num = month.split('-')
            month_name = calendar.month_name[int(month_num)]
            month_labels.append(f"{month_name[:3]} {year}")
        except:
            month_labels.append(month)
    
    activity_datasets = []
    colors = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6']
    
    for i, activity_type in enumerate(sorted(activity_types)):
        data = []
        for month in sorted_months:
            data.append(months[month].get(activity_type, 0))
        
        activity_datasets.append({
            'label': activity_type.title(),
            'data': data,
            'backgroundColor': colors[i % len(colors)],
            'borderColor': colors[i % len(colors)]
        })
    
    return jsonify({
        'crop_distribution': {
            'labels': crop_labels,
            'counts': crop_counts,
            'areas': crop_areas,
            'colors': crop_colors[:len(crop_labels)]
        },
        'monthly_activities': {
            'labels': month_labels,
            'datasets': activity_datasets
        },
        'disease_detections': {
            'total': DiseaseDetection.query.join(Crop).join(Farm).filter(
                Farm.user_id == current_user.id
            ).count(),
            'healthy': DiseaseDetection.query.join(Crop).join(Farm).filter(
                Farm.user_id == current_user.id,
                DiseaseDetection.is_healthy == True
            ).count()
        }
    })

@api_bp.route('/dashboard-overview')
@login_required
def dashboard_overview_simple():
    """Simple route alias for dashboard overview data."""
    return dashboard_overview_data()

@api_bp.route('/weather-trends')
@login_required
def weather_trends_simple():
    """Simple route alias for weather trends data."""
    return weather_trends_data()
