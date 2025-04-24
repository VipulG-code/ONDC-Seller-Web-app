from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField, SelectField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional, ValidationError
from flask_login import current_user

class BusinessProfileForm(FlaskForm):
    """Form for business profile settings."""
    business_name = StringField('Business Name', validators=[DataRequired(), Length(2, 100)])
    owner_name = StringField('Owner Name', validators=[DataRequired(), Length(2, 100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone Number', validators=[Length(0, 20)])
    
    address = TextAreaField('Address', validators=[Optional()])
    city = StringField('City', validators=[Optional(), Length(max=100)])
    state = StringField('State', validators=[Optional(), Length(max=100)])
    postal_code = StringField('Postal Code', validators=[Optional(), Length(max=20)])
    country = StringField('Country', validators=[Optional(), Length(max=100)])
    
    business_category = SelectField('Business Category', choices=[
        ('', 'Select a category'),
        ('retail', 'Retail'),
        ('grocery', 'Grocery'),
        ('food_beverage', 'Food & Beverage'),
        ('electronics', 'Electronics'),
        ('clothing', 'Clothing & Apparel'),
        ('health_beauty', 'Health & Beauty'),
        ('home_furniture', 'Home & Furniture'),
        ('other', 'Other')
    ])
    
    tax_id = StringField('Tax ID / GST Number', validators=[Optional(), Length(max=50)])
    
    submit = SubmitField('Update Profile')


class PasswordChangeForm(FlaskForm):
    """Form for changing password."""
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[
        DataRequired(),
        Length(min=8, message='Password must be at least 8 characters long.')
    ])
    confirm_password = PasswordField('Confirm New Password', validators=[
        DataRequired(),
        EqualTo('new_password', message='Passwords must match.')
    ])
    
    submit = SubmitField('Change Password')


class OndcSettingsForm(FlaskForm):
    """Form for ONDC integration settings."""
    ondc_seller_id = StringField('ONDC Seller ID', validators=[Optional(), Length(max=100)])
    ondc_provider_id = StringField('ONDC Provider ID', validators=[Optional(), Length(max=100)])
    ondc_location_id = StringField('ONDC Location ID', validators=[Optional(), Length(max=100)])
    ondc_api_key = StringField('ONDC API Key', validators=[Optional(), Length(max=100)])
    ondc_api_url = StringField('ONDC API URL', validators=[Optional(), Length(max=255)])
    ondc_enabled = BooleanField('Enable ONDC Integration')
    
    submit = SubmitField('Save ONDC Settings')
