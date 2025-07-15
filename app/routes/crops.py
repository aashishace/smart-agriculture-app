"""
Crop Management Routes
"""

from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from flask_babel import gettext as _
from app.models.farm import Farm
from app.models.crop import Crop, Activity
from app.services.irrigation import IrrigationService
from app.services.notifications import NotificationService
from app.services.activity_templates import ActivityTemplateService
from app import db
from datetime import date, datetime, timedelta
import json

crops_bp = Blueprint('crops', __name__)

@crops_bp.route('/')
@login_required
def index():
    """List all crops."""
    farms = current_user.farms.all()
    all_crops = []
    
    for farm in farms:
        crops = farm.get_active_crops()
        for crop in crops:
            # Add farm_name as an attribute instead of converting to dict
            crop.farm_name = farm.farm_name
            all_crops.append(crop)
    
    return render_template('crops/index.html', crops=all_crops, farms=farms)

@crops_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_crop():
    """Add new crop."""
    farms = current_user.farms.all()
    
    if not farms:
        flash(_('Please add a farm first.'), 'warning')
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        farm_id = request.form.get('farm_id')
        crop_type = request.form.get('crop_type', '').strip().lower()
        variety = request.form.get('variety', '').strip()
        area_acres = request.form.get('area_acres')
        planting_date = request.form.get('planting_date')
        
        # Validation
        errors = []
        
        if not farm_id or not farm_id.isdigit():
            errors.append(_('Please select a farm.'))
        else:
            farm = Farm.query.filter_by(id=int(farm_id), user_id=current_user.id).first()
            if not farm:
                errors.append(_('Invalid farm.'))
        
        supported_crops = ['wheat', 'rice', 'sugarcane', 'corn', 'cotton']
        if not crop_type or crop_type not in supported_crops:
            errors.append(_('Please select a supported crop.'))
        
        try:
            area_acres = float(area_acres)
            if area_acres <= 0 or area_acres > 1000:
                errors.append(_('Area must be between 0 and 1000 acres.'))
        except (ValueError, TypeError):
            errors.append(_('Please enter valid area.'))
            area_acres = 0
        
        try:
            planting_date = datetime.strptime(planting_date, '%Y-%m-%d').date()
            if planting_date > date.today():
                errors.append(_('Planting date must be before today.'))
        except (ValueError, TypeError):
            errors.append(_('Please enter valid planting date.'))
            planting_date = None
        
        # Check if farm has enough space
        if not errors and farm:
            available_area = farm.get_available_area()
            if area_acres > available_area:
                errors.append(_('Available area is only %(area).1f acres.', area=available_area))
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('crops/add.html', farms=farms, date=date)
        
        # Create crop
        try:
            # Calculate expected harvest date based on crop type
            harvest_days = {
                'wheat': 140,
                'rice': 150,
                'sugarcane': 365,
                'corn': 120,
                'cotton': 180
            }
            
            expected_harvest = planting_date + timedelta(days=harvest_days.get(crop_type, 120))
            
            crop = Crop(
                farm_id=farm.id,
                crop_type=crop_type,
                variety=variety,
                area_acres=area_acres,
                planting_date=planting_date,
                expected_harvest_date=expected_harvest
            )
            
            db.session.add(crop)
            db.session.commit()
            
            # Auto-create activity schedule from templates
            activity_service = ActivityTemplateService()
            created_activities = activity_service.create_activities_from_template(
                crop, 
                current_user.preferred_language or 'hi'
            )
            
            if created_activities:
                flash(_('Crop added successfully. %(count)d activities scheduled automatically.', count=len(created_activities)), 'success')
            else:
                flash(_('Crop added successfully.'), 'success')
                
            return redirect(url_for('crops.view', crop_id=crop.id))
            
        except Exception as e:
            db.session.rollback()
            flash(_('Error adding crop.'), 'error')
    
    return render_template('crops/add.html', farms=farms, date=date)

@crops_bp.route('/<int:crop_id>')
@login_required
def view(crop_id):
    """View crop details."""
    crop = Crop.query.join(Farm).filter(
        Crop.id == crop_id,
        Farm.user_id == current_user.id
    ).first_or_404()
    
    # Get recent activities
    recent_activities = crop.get_recent_activities(10)
    
    # Get irrigation recommendation
    irrigation_service = IrrigationService()
    farm_location = crop.farm.get_location()
    irrigation_recommendation = irrigation_service.calculate_irrigation_need(crop, farm_location)
    
    return render_template('crops/view.html', 
                         crop=crop,
                         recent_activities=recent_activities,
                         irrigation_recommendation=irrigation_recommendation)

@crops_bp.route('/<int:crop_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(crop_id):
    """Edit crop details."""
    crop = Crop.query.join(Farm).filter(
        Crop.id == crop_id,
        Farm.user_id == current_user.id
    ).first_or_404()
    
    if request.method == 'POST':
        variety = request.form.get('variety', '').strip()
        current_stage = request.form.get('current_stage', '').strip()
        status = request.form.get('status', 'active')
        
        try:
            crop.variety = variety
            crop.current_stage = current_stage
            crop.status = status
            
            db.session.commit()
            flash(_('Crop information updated successfully.'), 'success')
            return redirect(url_for('crops.view', crop_id=crop.id))
            
        except Exception as e:
            db.session.rollback()
            flash(_('Error updating crop.'), 'error')
    
    return render_template('crops/edit.html', crop=crop)

@crops_bp.route('/<int:crop_id>/activities')
@login_required
def activities(crop_id):
    """View crop activities."""
    crop = Crop.query.join(Farm).filter(
        Crop.id == crop_id,
        Farm.user_id == current_user.id
    ).first_or_404()
    
    # Get activities with pagination
    page = request.args.get('page', 1, type=int)
    activities = crop.activities.order_by(Activity.scheduled_date.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('crops/activities.html', crop=crop, activities=activities)

@crops_bp.route('/<int:crop_id>/add-activity', methods=['GET', 'POST'])
@login_required
def add_activity(crop_id):
    """Add activity to crop."""
    crop = Crop.query.join(Farm).filter(
        Crop.id == crop_id,
        Farm.user_id == current_user.id
    ).first_or_404()
    
    if request.method == 'POST':
        activity_type = request.form.get('activity_type', '').strip()
        description = request.form.get('description', '').strip()
        quantity = request.form.get('quantity', '').strip()
        scheduled_date = request.form.get('scheduled_date')
        
        # Validation
        if not activity_type or activity_type not in ['irrigation', 'fertilizer', 'pesticide', 'harvesting', 'other']:
            flash(_('Please select activity type.'), 'error')
            return render_template('crops/add_activity.html', crop=crop)
        
        try:
            scheduled_date = datetime.strptime(scheduled_date, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            flash(_('Please enter valid date.'), 'error')
            return render_template('crops/add_activity.html', crop=crop)
        
        try:
            activity = Activity(
                crop_id=crop.id,
                activity_type=activity_type,
                description=description,
                quantity=quantity,
                scheduled_date=scheduled_date
            )
            
            db.session.add(activity)
            db.session.commit()
            
            flash(_('Activity added successfully.'), 'success')
            return redirect(url_for('crops.activities', crop_id=crop.id))
            
        except Exception as e:
            db.session.rollback()
            flash(_('Error adding activity.'), 'error')
    
    return render_template('crops/add_activity.html', crop=crop)

@crops_bp.route('/bulk-activities', methods=['GET', 'POST'])
@login_required
def bulk_activities():
    """Bulk activity creation for multiple crops."""
    farms = current_user.farms.all()
    
    if request.method == 'POST':
        selected_crops = request.form.getlist('crop_ids')
        activity_type = request.form.get('activity_type', '').strip()
        description = request.form.get('description', '').strip()
        quantity = request.form.get('quantity', '').strip()
        scheduled_date = request.form.get('scheduled_date')
        
        if not selected_crops:
            flash(_('Please select at least one crop.'), 'error')
            return render_template('crops/bulk_activities.html', farms=farms)
        
        if not activity_type:
            flash(_('Please select activity type.'), 'error')
            return render_template('crops/bulk_activities.html', farms=farms)
        
        try:
            scheduled_date = datetime.strptime(scheduled_date, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            flash(_('Please enter valid date.'), 'error')
            return render_template('crops/bulk_activities.html', farms=farms)
        
        # Create activities for selected crops
        created_count = 0
        for crop_id in selected_crops:
            crop = Crop.query.join(Farm).filter(
                Crop.id == int(crop_id),
                Farm.user_id == current_user.id
            ).first()
            
            if crop:
                activity = Activity(
                    crop_id=crop.id,
                    activity_type=activity_type,
                    description=description,
                    quantity=quantity,
                    scheduled_date=scheduled_date
                )
                db.session.add(activity)
                created_count += 1
        
        if created_count > 0:
            db.session.commit()
            flash(_('Activity added for %(count)d crops.', count=created_count), 'success')
        else:
            flash(_('No activities were added.'), 'error')
        
        return redirect(url_for('crops.index'))
    
    # GET request - show form
    activity_service = ActivityTemplateService()
    activity_types = activity_service.get_activity_types()
    
    return render_template('crops/bulk_activities.html', farms=farms, activity_types=activity_types)

@crops_bp.route('/api/activity-suggestions/<int:crop_id>')
@login_required  
def activity_suggestions(crop_id):
    """API endpoint for activity suggestions based on crop stage."""
    crop = Crop.query.join(Farm).filter(
        Crop.id == crop_id,
        Farm.user_id == current_user.id
    ).first_or_404()
    
    activity_service = ActivityTemplateService()
    suggestions = activity_service.get_suggested_activities(crop)
    
    return jsonify({
        'suggestions': suggestions,
        'crop_stage': crop.get_growth_stage_info()
    })

@crops_bp.route('/generate-schedule/<int:crop_id>', methods=['POST'])
@login_required
def generate_schedule(crop_id):
    """Generate complete activity schedule for a crop."""
    crop = Crop.query.join(Farm).filter(
        Crop.id == crop_id,
        Farm.user_id == current_user.id
    ).first_or_404()
    
    activity_service = ActivityTemplateService()
    created_activities = activity_service.create_activities_from_template(
        crop,
        current_user.preferred_language or 'hi'
    )
    
    if created_activities:
        flash(_('%(count)d activities scheduled automatically.', count=len(created_activities)), 'success')
    else:
        flash(_('All activities already exist.'), 'info')
    
    return redirect(url_for('crops.activities', crop_id=crop.id))

@crops_bp.route('/activity/<int:activity_id>/complete', methods=['POST'])
@login_required
def complete_activity(activity_id):
    """Mark activity as completed."""
    activity = Activity.query.join(Crop).join(Farm).filter(
        Activity.id == activity_id,
        Farm.user_id == current_user.id
    ).first_or_404()
    
    notes = request.form.get('notes', '').strip()
    
    try:
        activity.mark_completed(notes)
        flash(_('Activity marked as completed.'), 'success')
    except Exception as e:
        flash(_('An error occurred.'), 'error')
    
    return redirect(url_for('crops.activities', crop_id=activity.crop_id))

@crops_bp.route('/api/<int:crop_id>/irrigation-recommendation')
@login_required
def irrigation_recommendation_api(crop_id):
    """API endpoint for irrigation recommendation."""
    crop = Crop.query.join(Farm).filter(
        Crop.id == crop_id,
        Farm.user_id == current_user.id
    ).first_or_404()
    
    irrigation_service = IrrigationService()
    farm_location = crop.farm.get_location()
    recommendation = irrigation_service.calculate_irrigation_need(crop, farm_location)
    
    return jsonify(recommendation)

@crops_bp.route('/api/<int:crop_id>/schedule-irrigation', methods=['POST'])
@login_required
def schedule_irrigation_api(crop_id):
    """API endpoint to schedule irrigation."""
    crop = Crop.query.join(Farm).filter(
        Crop.id == crop_id,
        Farm.user_id == current_user.id
    ).first_or_404()
    
    data = request.get_json()
    water_amount = data.get('water_amount_mm', 0)
    
    if water_amount <= 0:
        return jsonify({'error': 'Invalid water amount'}), 400
    
    try:
        irrigation_service = IrrigationService()
        activity = irrigation_service.schedule_irrigation_activity(crop, water_amount)
        
        # Send notification
        notification_service = NotificationService()
        notification_service.send_irrigation_alert(
            current_user.phone,
            crop.crop_type,
            f"आज {water_amount}मिमी पानी दें",
            current_user.preferred_language
        )
        
        return jsonify({
            'success': True,
            'activity_id': activity.id,
            'message': 'सिंचाई निर्धारित की गई और SMS भेजा गया'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
