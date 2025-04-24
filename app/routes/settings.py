from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models.user import User
from app.models.customer import ShippingMethod, Setting
from app.forms.settings import BusinessProfileForm, PasswordChangeForm, OndcSettingsForm

settings_bp = Blueprint('settings', __name__, url_prefix='/settings')

@settings_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """Manage business profile settings."""
    form = BusinessProfileForm(obj=current_user)
    
    if form.validate_on_submit():
        current_user.business_name = form.business_name.data
        current_user.owner_name = form.owner_name.data
        current_user.email = form.email.data
        current_user.phone = form.phone.data
        current_user.address = form.address.data
        current_user.city = form.city.data
        current_user.state = form.state.data
        current_user.postal_code = form.postal_code.data
        current_user.country = form.country.data
        current_user.business_category = form.business_category.data
        current_user.tax_id = form.tax_id.data
        
        db.session.commit()
        flash('Profile updated successfully', 'success')
        return redirect(url_for('settings.profile'))
    
    return render_template('settings/profile.html',
                          title='Business Profile',
                          form=form)

@settings_bp.route('/security', methods=['GET', 'POST'])
@login_required
def security():
    """Manage security settings like password change."""
    form = PasswordChangeForm()
    
    if form.validate_on_submit():
        if current_user.check_password(form.current_password.data):
            current_user.password = form.new_password.data
            db.session.commit()
            flash('Password changed successfully', 'success')
            return redirect(url_for('settings.security'))
        else:
            flash('Current password is incorrect', 'danger')
    
    return render_template('settings/security.html',
                          title='Security Settings',
                          form=form)

@settings_bp.route('/shipping', methods=['GET', 'POST'])
@login_required
def shipping():
    """Manage shipping methods and zones."""
    shipping_methods = ShippingMethod.query.all()
    
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        price = request.form.get('price', type=float)
        estimated_days = request.form.get('estimated_days')
        
        if name and price is not None:
            shipping_method = ShippingMethod(
                name=name,
                description=description,
                price=price,
                estimated_days=estimated_days
            )
            db.session.add(shipping_method)
            db.session.commit()
            
            flash('Shipping method added successfully', 'success')
            return redirect(url_for('settings.shipping'))
    
    return render_template('settings/shipping.html',
                          title='Shipping Settings',
                          shipping_methods=shipping_methods)

@settings_bp.route('/shipping/delete/<int:id>', methods=['POST'])
@login_required
def delete_shipping(id):
    """Delete a shipping method."""
    shipping_method = ShippingMethod.query.get_or_404(id)
    
    db.session.delete(shipping_method)
    db.session.commit()
    
    flash('Shipping method deleted successfully', 'success')
    return redirect(url_for('settings.shipping'))

@settings_bp.route('/ondc', methods=['GET', 'POST'])
@login_required
def ondc():
    """Manage ONDC integration settings."""
    # Get existing ONDC settings
    ondc_settings = {}
    settings = Setting.query.filter_by(user_id=current_user.id).all()
    for setting in settings:
        if setting.key.startswith('ondc_'):
            ondc_settings[setting.key] = setting.value
    
    form = OndcSettingsForm(data=ondc_settings)
    
    if form.validate_on_submit():
        # Save ONDC settings
        for field in form:
            if field.name.startswith('ondc_'):
                setting = Setting.query.filter_by(
                    user_id=current_user.id,
                    key=field.name
                ).first()
                
                if not setting:
                    setting = Setting(user_id=current_user.id, key=field.name)
                
                setting.value = field.data
                db.session.add(setting)
        
        db.session.commit()
        flash('ONDC settings updated successfully', 'success')
        return redirect(url_for('settings.ondc'))
    
    return render_template('settings/ondc.html',
                          title='ONDC Configuration',
                          form=form)

@settings_bp.route('/notifications')
@login_required
def notifications():
    """Manage notification preferences."""
    # Get current notification settings
    notification_settings = {}
    settings = Setting.query.filter_by(user_id=current_user.id).all()
    for setting in settings:
        if setting.key.startswith('notify_'):
            notification_settings[setting.key] = setting.value == 'true'
    
    # Default settings if none exist
    if not notification_settings:
        notification_settings = {
            'notify_new_order': True,
            'notify_order_status': True,
            'notify_low_stock': True,
            'notify_customer_message': True,
            'notify_email': True,
            'notify_app': True
        }
    
    if request.method == 'POST':
        # Update notification settings
        for key in notification_settings:
            value = 'true' if request.form.get(key) else 'false'
            
            setting = Setting.query.filter_by(
                user_id=current_user.id,
                key=key
            ).first()
            
            if not setting:
                setting = Setting(user_id=current_user.id, key=key)
            
            setting.value = value
            db.session.add(setting)
        
        db.session.commit()
        flash('Notification preferences updated', 'success')
        return redirect(url_for('settings.notifications'))
    
    return render_template('settings/notifications.html',
                          title='Notification Preferences',
                          settings=notification_settings)
