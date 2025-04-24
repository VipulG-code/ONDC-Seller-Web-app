from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Regexp, ValidationError
from app.models.user import User

class LoginForm(FlaskForm):
    """Form for user login."""
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Log In')

class RegistrationForm(FlaskForm):
    """Form for user registration."""
    username = StringField('Username', validators=[
        DataRequired(),
        Length(3, 64),
        Regexp('^[A-Za-z0-9_-]*$', message='Username can only contain letters, numbers, underscores, and dashes.')
    ])
    email = StringField('Email', validators=[DataRequired(), Email()])
    business_name = StringField('Business Name', validators=[DataRequired(), Length(2, 100)])
    owner_name = StringField('Owner Name', validators=[DataRequired(), Length(2, 100)])
    phone = StringField('Phone Number', validators=[Length(0, 20)])
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
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=8, message='Password must be at least 8 characters long.')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match.')
    ])
    agree_terms = BooleanField('I agree to the Terms and Conditions', validators=[DataRequired()])
    submit = SubmitField('Register')
    
    def validate_username(self, field):
        """Check if username is already in use."""
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')
    
    def validate_email(self, field):
        """Check if email is already registered."""
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

class ForgotPasswordForm(FlaskForm):
    """Form for password reset request."""
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Reset Password')

class ResetPasswordForm(FlaskForm):
    """Form for setting a new password after reset."""
    password = PasswordField('New Password', validators=[
        DataRequired(),
        Length(min=8, message='Password must be at least 8 characters long.')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match.')
    ])
    submit = SubmitField('Set New Password')
