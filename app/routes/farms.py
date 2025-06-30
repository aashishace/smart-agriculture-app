"""
Farm Management Routes
"""

from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from flask_babel import gettext as _
from app.models.farm import Farm
from app.models.crop import Crop
from app import db
from datetime import datetime
import re

farms_bp = Blueprint('farms', __name__, url_prefix='/farms')

@farms_bp.route('/')
@login_required
def index():
    """List all user's farms."""
    farms = current_user.farms.order_by(Farm.created_at.desc()).all()
    
    # Calculate statistics
    total_area = sum(float(farm.area_acres) for farm in farms)
    total_crops = sum(len(farm.get_active_crops()) for farm in farms)
    farms_with_gps = sum(1 for farm in farms if farm.is_location_set())
    
    stats = {
        'total_farms': len(farms),
        'total_area': total_area,
        'total_crops': total_crops,
        'farms_with_gps': farms_with_gps
    }
    
    return render_template('farms/index.html', farms=farms, stats=stats)

@farms_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    """Add new farm."""
    if request.method == 'POST':
        farm_name = request.form.get('farm_name', '').strip()
        area_acres = request.form.get('area_acres', '').strip()
        soil_type = request.form.get('soil_type', '').strip()
        latitude = request.form.get('latitude', '').strip()
        longitude = request.form.get('longitude', '').strip()
        
        # Validation
        errors = []
        
        if not farm_name or len(farm_name) < 2:
            errors.append(_('Farm name must be at least 2 characters long.'))
        
        try:
            area_acres = float(area_acres)
            if area_acres <= 0 or area_acres > 10000:
                errors.append(_('Area must be between 0 and 10000 acres.'))
        except (ValueError, TypeError):
            errors.append(_('Please enter valid area.'))
            area_acres = 0
        
        # GPS coordinates validation (optional)
        lat_val = None
        lon_val = None
        if latitude and longitude:
            try:
                lat_val = float(latitude)
                lon_val = float(longitude)
                if not (-90 <= lat_val <= 90) or not (-180 <= lon_val <= 180):
                    errors.append(_('Please enter valid GPS coordinates.'))
            except (ValueError, TypeError):
                errors.append(_('GPS coordinates must be numbers.'))
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('farms/add.html')
        
        # Create farm
        try:
            farm = Farm(
                user_id=current_user.id,
                farm_name=farm_name,
                area_acres=area_acres,
                soil_type=soil_type,
                latitude=lat_val,
                longitude=lon_val
            )
            
            db.session.add(farm)
            db.session.commit()
            
            flash(_('Farm added successfully.'), 'success')
            return redirect(url_for('farms.view', farm_id=farm.id))
            
        except Exception as e:
            db.session.rollback()
            flash(_('Error adding farm.'), 'error')
    
    return render_template('farms/add.html')

@farms_bp.route('/<int:farm_id>')
@login_required
def view(farm_id):
    """View farm details."""
    farm = Farm.query.filter_by(id=farm_id, user_id=current_user.id).first_or_404()
    
    # Get active crops in this farm
    active_crops = farm.get_active_crops()
    
    # Calculate statistics
    stats = {
        'total_crops': len(active_crops),
        'total_area_used': farm.get_total_crops_area(),
        'available_area': farm.get_available_area(),
        'utilization_percent': (farm.get_total_crops_area() / float(farm.area_acres)) * 100 if farm.area_acres > 0 else 0
    }
    
    return render_template('farms/view.html', farm=farm, active_crops=active_crops, stats=stats)

@farms_bp.route('/<int:farm_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(farm_id):
    """Edit farm details."""
    farm = Farm.query.filter_by(id=farm_id, user_id=current_user.id).first_or_404()
    
    if request.method == 'POST':
        farm_name = request.form.get('farm_name', '').strip()
        soil_type = request.form.get('soil_type', '').strip()
        latitude = request.form.get('latitude', '').strip()
        longitude = request.form.get('longitude', '').strip()
        
        # Validation
        if not farm_name or len(farm_name) < 2:
            flash(_('Farm name must be at least 2 characters long.'), 'error')
            return render_template('farms/edit.html', farm=farm)
        
        # GPS coordinates validation (optional)
        lat_val = farm.latitude
        lon_val = farm.longitude
        if latitude and longitude:
            try:
                lat_val = float(latitude)
                lon_val = float(longitude)
                if not (-90 <= lat_val <= 90) or not (-180 <= lon_val <= 180):
                    flash(_('Please enter valid GPS coordinates.'), 'error')
                    return render_template('farms/edit.html', farm=farm)
            except (ValueError, TypeError):
                flash(_('GPS coordinates must be numbers.'), 'error')
                return render_template('farms/edit.html', farm=farm)
        elif latitude == '' and longitude == '':
            # Clear coordinates if both are empty
            lat_val = None
            lon_val = None
        
        try:
            farm.farm_name = farm_name
            farm.soil_type = soil_type
            farm.latitude = lat_val
            farm.longitude = lon_val
            
            db.session.commit()
            flash(_('Farm information updated successfully.'), 'success')
            return redirect(url_for('farms.view', farm_id=farm.id))
            
        except Exception as e:
            db.session.rollback()
            flash(_('Error updating farm.'), 'error')
    
    return render_template('farms/edit.html', farm=farm)

@farms_bp.route('/<int:farm_id>/delete', methods=['POST'])
@login_required
def delete(farm_id):
    """Delete farm (with confirmation)."""
    farm = Farm.query.filter_by(id=farm_id, user_id=current_user.id).first_or_404()
    
    # Check if farm has active crops
    active_crops = farm.get_active_crops()
    if active_crops:
        flash(_('First remove or complete all %(count)d crops.', count=len(active_crops)), 'error')
        return redirect(url_for('farms.view', farm_id=farm.id))
    
    try:
        farm_name = farm.farm_name
        db.session.delete(farm)
        db.session.commit()
        
        flash(_('Farm "%(name)s" deleted successfully.', name=farm_name), 'success')
        return redirect(url_for('farms.index'))
        
    except Exception as e:
        db.session.rollback()
        flash(_('Error deleting farm.'), 'error')
        return redirect(url_for('farms.view', farm_id=farm.id))

@farms_bp.route('/api/location-suggestions')
@login_required
def location_suggestions():
    """API endpoint for location-based suggestions."""
    query = request.args.get('q', '').strip()
    
    if len(query) < 3:
        return jsonify([])
    
    # In a real app, you'd integrate with a geocoding service
    # For now, return some sample suggestions
    suggestions = [
        {'name': f'{query} - उत्तर प्रदेश', 'lat': 26.8467, 'lon': 80.9462},
        {'name': f'{query} - बिहार', 'lat': 25.0961, 'lon': 85.3131},
        {'name': f'{query} - मध्य प्रदेश', 'lat': 22.9734, 'lon': 78.6569},
    ]
    
    return jsonify(suggestions)
