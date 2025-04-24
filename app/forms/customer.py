
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired, Email, Optional

class CustomerForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone', validators=[Optional()])
    address = TextAreaField('Address', validators=[Optional()])
    city = StringField('City', validators=[Optional()])
    state = StringField('State', validators=[Optional()])
    postal_code = StringField('Postal Code', validators=[Optional()])
    country = StringField('Country', validators=[Optional()])
    notes = TextAreaField('Notes', validators=[Optional()])
