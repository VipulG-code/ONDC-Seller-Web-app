from flask_wtf import FlaskForm
from flask_wtf.file import FileField, MultipleFileField
from wtforms import StringField, TextAreaField, FloatField, IntegerField, SelectField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange, Optional
from app.models.product import Category

class ProductForm(FlaskForm):
    """Form for adding or editing a product."""
    # Basic info
    name = StringField('Product Name', validators=[DataRequired(), Length(2, 255)])
    sku = StringField('SKU (Stock Keeping Unit)', validators=[DataRequired(), Length(2, 50)])
    description = TextAreaField('Description')
    short_description = TextAreaField('Short Description', validators=[Optional(), Length(max=500)])
    
    # Pricing
    price = IntegerField('Selling Price', validators=[DataRequired(), NumberRange(min=0)])
    mrp = IntegerField('MRP (Maximum Retail Price)', validators=[DataRequired(), NumberRange(min=0)])
    cost_price = IntegerField('Cost Price', validators=[Optional(), NumberRange(min=0)])
    tax_rate = IntegerField('Tax Rate (%)', validators=[Optional(), NumberRange(min=0, max=100)], default=0)
    
    # Inventory
    stock_quantity = IntegerField('Stock Quantity', validators=[Optional(), NumberRange(min=0)], default=0)
    low_stock_threshold = IntegerField('Low Stock Alert Threshold', validators=[Optional(), NumberRange(min=0)], default=5)
    
    # Physical attributes
    weight = FloatField('Weight (kg)', validators=[Optional(), NumberRange(min=0)])
    length = FloatField('Length (cm)', validators=[Optional(), NumberRange(min=0)])
    width = FloatField('Width (cm)', validators=[Optional(), NumberRange(min=0)])
    height = FloatField('Height (cm)', validators=[Optional(), NumberRange(min=0)])
    
    # Status and category
    status = SelectField('Status', choices=[
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('inactive', 'Inactive')
    ], default='draft')
    featured = BooleanField('Featured Product')
    category_id = SelectField('Category', coerce=int, validators=[Optional()])
    
    # ONDC specific fields
    hsn_code = StringField('HSN Code', validators=[Optional(), Length(max=50)])
    ondc_category = StringField('ONDC Category', validators=[Optional(), Length(max=100)])
    fulfillment_id = StringField('Fulfillment ID', validators=[Optional(), Length(max=100)])
    
    # Images
    images = MultipleFileField('Product Images')
    
    # Submit
    submit = SubmitField('Save Product')
    
    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        self.category_id.choices = [(0, 'None')] + [(c.id, c.name) for c in Category.query.all()]


class CategoryForm(FlaskForm):
    """Form for adding or editing a product category."""
    name = StringField('Category Name', validators=[DataRequired(), Length(2, 100)])
    description = TextAreaField('Description', validators=[Optional()])
    parent_id = SelectField('Parent Category', coerce=int, validators=[Optional()])
    submit = SubmitField('Save Category')
    
    def __init__(self, *args, **kwargs):
        super(CategoryForm, self).__init__(*args, **kwargs)
        self.parent_id.choices = [(0, 'None')] + [(c.id, c.name) for c in Category.query.all()]
