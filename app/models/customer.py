from datetime import datetime
from app import db

class Customer(db.Model):
    """Customer information model."""
    __tablename__ = 'customers'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(20), nullable=True)
    address = db.Column(db.Text, nullable=True)
    city = db.Column(db.String(100), nullable=True)
    state = db.Column(db.String(100), nullable=True)
    postal_code = db.Column(db.String(20), nullable=True)
    country = db.Column(db.String(100), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    orders = db.relationship('Order', backref='customer', lazy='dynamic')
    
    def get_total_orders(self):
        return self.orders.count()
    
    def get_total_spent(self):
        total = 0
        for order in self.orders.all():
            if order.payment_status == 'paid':
                total += order.total_amount
        return total
    
    def __repr__(self):
        return f'<Customer {self.name}>'

class ShippingMethod(db.Model):
    """Available shipping methods model."""
    __tablename__ = 'shipping_methods'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, default=0.0)
    is_active = db.Column(db.Boolean, default=True)
    estimated_days = db.Column(db.String(50), nullable=True)  # e.g., "3-5 days"
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    zones = db.relationship('ShippingZone', backref='shipping_method', lazy='dynamic')
    
    def __repr__(self):
        return f'<ShippingMethod {self.name}>'

class ShippingZone(db.Model):
    """Delivery zones with rates model."""
    __tablename__ = 'shipping_zones'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    regions = db.Column(db.JSON, nullable=True)  # Store regions (states, countries) as JSON
    rate = db.Column(db.Float, default=0.0)
    shipping_method_id = db.Column(db.Integer, db.ForeignKey('shipping_methods.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<ShippingZone {self.name}>'

class Promotion(db.Model):
    """Marketing promotions and discounts model."""
    __tablename__ = 'promotions'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    code = db.Column(db.String(50), unique=True, nullable=True)  # Coupon code
    discount_type = db.Column(db.String(20), nullable=False)  # percentage, fixed
    discount_value = db.Column(db.Float, nullable=False)
    start_date = db.Column(db.DateTime, nullable=True)
    end_date = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    usage_limit = db.Column(db.Integer, nullable=True)  # Max number of uses
    usage_count = db.Column(db.Integer, default=0)
    minimum_order_amount = db.Column(db.Float, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def is_valid(self, order_amount=None):
        now = datetime.utcnow()
        if not self.is_active:
            return False
        if self.start_date and now < self.start_date:
            return False
        if self.end_date and now > self.end_date:
            return False
        if self.usage_limit and self.usage_count >= self.usage_limit:
            return False
        if order_amount and self.minimum_order_amount and order_amount < self.minimum_order_amount:
            return False
        return True
    
    def __repr__(self):
        return f'<Promotion {self.name}>'

class Notification(db.Model):
    """System notifications model."""
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(20), nullable=True)  # info, warning, error, success
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='notifications')
    
    def __repr__(self):
        return f'<Notification {self.title}>'

class Setting(db.Model):
    """System and user settings model."""
    __tablename__ = 'settings'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # If NULL, it's a system setting
    key = db.Column(db.String(100), nullable=False)
    value = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='settings')
    
    def __repr__(self):
        return f'<Setting {self.key}>'
