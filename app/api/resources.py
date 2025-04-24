from flask import request, jsonify, current_app
from flask_restful import Resource, reqparse, abort
from flask_login import current_user, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from datetime import datetime, timedelta
from app import db
from app.models.user import User
from app.models.product import Product, Category
from app.models.order import Order, OrderItem
from app.models.customer import Customer, ShippingMethod, ShippingZone, Promotion, Notification, Setting

# Helper for JWT authentication
def generate_token(user_id):
    """Generate a JWT token for the user."""
    payload = {
        'exp': datetime.utcnow() + timedelta(days=1),
        'iat': datetime.utcnow(),
        'sub': user_id
    }
    return jwt.encode(
        payload,
        current_app.config.get('SECRET_KEY'),
        algorithm='HS256'
    )

def verify_token(token):
    """Verify a JWT token and return the user_id."""
    try:
        payload = jwt.decode(
            token,
            current_app.config.get('SECRET_KEY'),
            algorithms=['HS256']
        )
        return payload['sub']
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

# Authentication Resources
class AuthLoginResource(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('email', required=True, help='Email is required')
        parser.add_argument('password', required=True, help='Password is required')
        args = parser.parse_args()
        
        user = User.query.filter_by(email=args['email']).first()
        if user and user.check_password(args['password']):
            token = generate_token(user.id)
            return {'token': token, 'user_id': user.id, 'email': user.email, 'username': user.username}
        
        return {'message': 'Invalid credentials'}, 401

class AuthRegisterResource(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('username', required=True, help='Username is required')
        parser.add_argument('email', required=True, help='Email is required')
        parser.add_argument('password', required=True, help='Password is required')
        parser.add_argument('business_name', required=True, help='Business name is required')
        parser.add_argument('owner_name', required=True, help='Owner name is required')
        parser.add_argument('phone', required=False)
        parser.add_argument('business_category', required=False)
        args = parser.parse_args()
        
        # Check if user already exists
        if User.query.filter_by(email=args['email']).first():
            return {'message': 'Email already registered'}, 400
        
        if User.query.filter_by(username=args['username']).first():
            return {'message': 'Username already taken'}, 400
        
        # Create new user
        user = User(
            username=args['username'],
            email=args['email'],
            business_name=args['business_name'],
            owner_name=args['owner_name'],
            phone=args.get('phone', ''),
            business_category=args.get('business_category', '')
        )
        user.password = args['password']
        
        db.session.add(user)
        db.session.commit()
        
        token = generate_token(user.id)
        return {'token': token, 'user_id': user.id, 'message': 'Registration successful'}

class AuthForgotPasswordResource(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('email', required=True, help='Email is required')
        args = parser.parse_args()
        
        user = User.query.filter_by(email=args['email']).first()
        if user:
            # In a real application, you would generate a token and send a reset email
            # For this example, we'll just return a success message
            pass
        
        # Always return success to prevent email enumeration
        return {'message': 'If your email is registered, you will receive password reset instructions'}

class AuthResetPasswordResource(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('token', required=True, help='Token is required')
        parser.add_argument('password', required=True, help='New password is required')
        args = parser.parse_args()
        
        # In a real application, you would validate the token and update the password
        # For this example, we'll just return a success message
        return {'message': 'Password reset successful'}

# Product Resources
class ProductListResource(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('search', location='args')
        parser.add_argument('category', type=int, location='args')
        parser.add_argument('status', location='args')
        parser.add_argument('page', type=int, default=1, location='args')
        parser.add_argument('per_page', type=int, default=10, location='args')
        parser.add_argument('token', location='headers')
        args = parser.parse_args()
        
        # Validate token
        user_id = verify_token(args.get('token'))
        if not user_id:
            return {'message': 'Unauthorized'}, 401
        
        # Base query for products owned by user
        query = Product.query.filter_by(seller_id=user_id)
        
        # Apply filters
        if args.get('search'):
            query = query.filter(
                (Product.name.ilike(f"%{args['search']}%")) | 
                (Product.sku.ilike(f"%{args['search']}%"))
            )
        
        if args.get('category'):
            query = query.filter_by(category_id=args['category'])
        
        if args.get('status'):
            query = query.filter_by(status=args['status'])
        
        # Paginate results
        page = args.get('page', 1)
        per_page = args.get('per_page', 10)
        products_page = query.paginate(page=page, per_page=per_page)
        
        # Prepare results
        products = []
        for product in products_page.items:
            products.append({
                'id': product.id,
                'name': product.name,
                'sku': product.sku,
                'price': product.price,
                'stock_quantity': product.stock_quantity,
                'status': product.status,
                'images': [{'id': img.id, 'path': img.image_path, 'is_primary': img.is_primary} 
                          for img in product.images]
            })
        
        return {
            'products': products,
            'page': products_page.page,
            'pages': products_page.pages,
            'total': products_page.total
        }
    
    def post(self):
        parser = reqparse.RequestParser()
        # Basic product info
        parser.add_argument('name', required=True, help='Product name is required')
        parser.add_argument('sku', required=True, help='SKU is required')
        parser.add_argument('description')
        parser.add_argument('short_description')
        parser.add_argument('price', type=float, required=True, help='Price is required')
        parser.add_argument('mrp', type=float, required=True, help='MRP is required')
        parser.add_argument('cost_price', type=float)
        parser.add_argument('tax_rate', type=float, default=0.0)
        parser.add_argument('stock_quantity', type=int, default=0)
        parser.add_argument('low_stock_threshold', type=int, default=5)
        # Physical attributes
        parser.add_argument('weight', type=float)
        parser.add_argument('length', type=float)
        parser.add_argument('width', type=float)
        parser.add_argument('height', type=float)
        # Status and categorization
        parser.add_argument('status', default='draft')
        parser.add_argument('featured', type=bool, default=False)
        parser.add_argument('category_id', type=int)
        # ONDC specific
        parser.add_argument('hsn_code')
        parser.add_argument('ondc_category')
        parser.add_argument('token', location='headers')
        args = parser.parse_args()
        
        # Validate token
        user_id = verify_token(args.get('token'))
        if not user_id:
            return {'message': 'Unauthorized'}, 401
        
        # Check if SKU already exists
        if Product.query.filter_by(sku=args['sku']).first():
            return {'message': 'SKU already exists'}, 400
        
        # Create product
        product = Product(
            seller_id=user_id,
            name=args['name'],
            sku=args['sku'],
            description=args.get('description'),
            short_description=args.get('short_description'),
            price=args['price'],
            mrp=args['mrp'],
            cost_price=args.get('cost_price'),
            tax_rate=args.get('tax_rate', 0.0),
            stock_quantity=args.get('stock_quantity', 0),
            low_stock_threshold=args.get('low_stock_threshold', 5),
            weight=args.get('weight'),
            length=args.get('length'),
            width=args.get('width'),
            height=args.get('height'),
            status=args.get('status', 'draft'),
            featured=args.get('featured', False),
            category_id=args.get('category_id'),
            hsn_code=args.get('hsn_code'),
            ondc_category=args.get('ondc_category')
        )
        
        db.session.add(product)
        db.session.commit()
        
        return {'id': product.id, 'message': 'Product created successfully'}

class ProductResource(Resource):
    def get(self, product_id):
        parser = reqparse.RequestParser()
        parser.add_argument('token', location='headers')
        args = parser.parse_args()
        
        # Validate token
        user_id = verify_token(args.get('token'))
        if not user_id:
            return {'message': 'Unauthorized'}, 401
        
        # Get product
        product = Product.query.filter_by(id=product_id, seller_id=user_id).first()
        if not product:
            return {'message': 'Product not found'}, 404
        
        # Prepare response
        product_data = {
            'id': product.id,
            'name': product.name,
            'sku': product.sku,
            'description': product.description,
            'short_description': product.short_description,
            'price': product.price,
            'mrp': product.mrp,
            'cost_price': product.cost_price,
            'tax_rate': product.tax_rate,
            'stock_quantity': product.stock_quantity,
            'low_stock_threshold': product.low_stock_threshold,
            'weight': product.weight,
            'length': product.length,
            'width': product.width,
            'height': product.height,
            'status': product.status,
            'featured': product.featured,
            'category_id': product.category_id,
            'hsn_code': product.hsn_code,
            'ondc_category': product.ondc_category,
            'created_at': product.created_at.isoformat(),
            'updated_at': product.updated_at.isoformat(),
            'images': [{'id': img.id, 'path': img.image_path, 'is_primary': img.is_primary} 
                      for img in product.images],
            'variants': [{'id': var.id, 'name': var.name, 'sku': var.sku, 'price': var.price, 
                         'stock_quantity': var.stock_quantity, 'attributes': var.attributes} 
                        for var in product.variants]
        }
        
        return product_data
    
    def put(self, product_id):
        parser = reqparse.RequestParser()
        # Basic product info
        parser.add_argument('name')
        parser.add_argument('sku')
        parser.add_argument('description')
        parser.add_argument('short_description')
        parser.add_argument('price', type=float)
        parser.add_argument('mrp', type=float)
        parser.add_argument('cost_price', type=float)
        parser.add_argument('tax_rate', type=float)
        parser.add_argument('stock_quantity', type=int)
        parser.add_argument('low_stock_threshold', type=int)
        # Physical attributes
        parser.add_argument('weight', type=float)
        parser.add_argument('length', type=float)
        parser.add_argument('width', type=float)
        parser.add_argument('height', type=float)
        # Status and categorization
        parser.add_argument('status')
        parser.add_argument('featured', type=bool)
        parser.add_argument('category_id', type=int)
        # ONDC specific
        parser.add_argument('hsn_code')
        parser.add_argument('ondc_category')
        parser.add_argument('token', location='headers')
        args = parser.parse_args()
        
        # Validate token
        user_id = verify_token(args.get('token'))
        if not user_id:
            return {'message': 'Unauthorized'}, 401
        
        # Get product
        product = Product.query.filter_by(id=product_id, seller_id=user_id).first()
        if not product:
            return {'message': 'Product not found'}, 404
        
        # Update fields if provided
        for key, value in args.items():
            if key != 'token' and value is not None:
                setattr(product, key, value)
        
        db.session.commit()
        return {'message': 'Product updated successfully'}
    
    def delete(self, product_id):
        parser = reqparse.RequestParser()
        parser.add_argument('token', location='headers')
        args = parser.parse_args()
        
        # Validate token
        user_id = verify_token(args.get('token'))
        if not user_id:
            return {'message': 'Unauthorized'}, 401
        
        # Get product
        product = Product.query.filter_by(id=product_id, seller_id=user_id).first()
        if not product:
            return {'message': 'Product not found'}, 404
        
        db.session.delete(product)
        db.session.commit()
        return {'message': 'Product deleted successfully'}

# Order Resources
class OrderListResource(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('status', location='args')
        parser.add_argument('search', location='args')
        parser.add_argument('date_from', location='args')
        parser.add_argument('date_to', location='args')
        parser.add_argument('page', type=int, default=1, location='args')
        parser.add_argument('per_page', type=int, default=20, location='args')
        parser.add_argument('token', location='headers')
        args = parser.parse_args()
        
        # Validate token
        user_id = verify_token(args.get('token'))
        if not user_id:
            return {'message': 'Unauthorized'}, 401
        
        # Base query for orders
        query = Order.query.filter_by(seller_id=user_id)
        
        # Apply filters
        if args.get('status'):
            query = query.filter_by(status=args['status'])
        
        if args.get('search'):
            query = query.filter(
                (Order.order_number.ilike(f"%{args['search']}%")) | 
                (Order.customer_name.ilike(f"%{args['search']}%")) |
                (Order.customer_email.ilike(f"%{args['search']}%"))
            )
        
        if args.get('date_from'):
            query = query.filter(Order.created_at >= args['date_from'])
        
        if args.get('date_to'):
            query = query.filter(Order.created_at <= args['date_to'])
        
        # Order by most recent first
        query = query.order_by(Order.created_at.desc())
        
        # Paginate results
        page = args.get('page', 1)
        per_page = args.get('per_page', 20)
        orders_page = query.paginate(page=page, per_page=per_page)
        
        # Prepare results
        orders = []
        for order in orders_page.items:
            orders.append({
                'id': order.id,
                'order_number': order.order_number,
                'status': order.status,
                'total_amount': order.total_amount,
                'payment_status': order.payment_status,
                'customer_name': order.customer_name,
                'customer_email': order.customer_email,
                'created_at': order.created_at.isoformat(),
                'items_count': order.items.count()
            })
        
        return {
            'orders': orders,
            'page': orders_page.page,
            'pages': orders_page.pages,
            'total': orders_page.total
        }

class OrderResource(Resource):
    def get(self, order_id):
        parser = reqparse.RequestParser()
        parser.add_argument('token', location='headers')
        args = parser.parse_args()
        
        # Validate token
        user_id = verify_token(args.get('token'))
        if not user_id:
            return {'message': 'Unauthorized'}, 401
        
        # Get order
        order = Order.query.filter_by(id=order_id, seller_id=user_id).first()
        if not order:
            return {'message': 'Order not found'}, 404
        
        # Prepare response
        order_data = {
            'id': order.id,
            'order_number': order.order_number,
            'status': order.status,
            'total_amount': order.total_amount,
            'tax_amount': order.tax_amount,
            'shipping_amount': order.shipping_amount,
            'discount_amount': order.discount_amount,
            'payment_method': order.payment_method,
            'payment_status': order.payment_status,
            'notes': order.notes,
            'created_at': order.created_at.isoformat(),
            'updated_at': order.updated_at.isoformat(),
            'customer_name': order.customer_name,
            'customer_email': order.customer_email,
            'customer_phone': order.customer_phone,
            'shipping_address': order.shipping_address,
            'shipping_city': order.shipping_city,
            'shipping_state': order.shipping_state,
            'shipping_postal_code': order.shipping_postal_code,
            'shipping_country': order.shipping_country,
            'shipping_method': order.shipping_method,
            'tracking_number': order.tracking_number,
            'items': []
        }
        
        # Add order items
        for item in order.items:
            order_data['items'].append({
                'id': item.id,
                'product_id': item.product_id,
                'product_name': item.product_name,
                'product_sku': item.product_sku,
                'quantity': item.quantity,
                'price': item.price,
                'tax_amount': item.tax_amount,
                'discount_amount': item.discount_amount,
                'total': item.total,
                'product_options': item.product_options
            })
        
        return order_data

class OrderStatusResource(Resource):
    def put(self, order_id):
        parser = reqparse.RequestParser()
        parser.add_argument('status', required=True, help='Status is required')
        parser.add_argument('token', location='headers')
        args = parser.parse_args()
        
        # Validate token
        user_id = verify_token(args.get('token'))
        if not user_id:
            return {'message': 'Unauthorized'}, 401
        
        # Get order
        order = Order.query.filter_by(id=order_id, seller_id=user_id).first()
        if not order:
            return {'message': 'Order not found'}, 404
        
        # Validate status
        status = args['status']
        if status not in ['new', 'processing', 'shipped', 'delivered', 'cancelled']:
            return {'message': 'Invalid status'}, 400
        
        order.status = status
        db.session.commit()
        
        return {'message': 'Order status updated successfully'}

# Customer Resources
class CustomerListResource(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('search', location='args')
        parser.add_argument('page', type=int, default=1, location='args')
        parser.add_argument('per_page', type=int, default=20, location='args')
        parser.add_argument('token', location='headers')
        args = parser.parse_args()
        
        # Validate token
        user_id = verify_token(args.get('token'))
        if not user_id:
            return {'message': 'Unauthorized'}, 401
        
        # Get customers with orders from this seller
        query = Customer.query.join(Order).filter(
            Order.seller_id == user_id
        ).distinct()
        
        # Apply search filter
        if args.get('search'):
            query = query.filter(
                (Customer.name.ilike(f"%{args['search']}%")) | 
                (Customer.email.ilike(f"%{args['search']}%")) |
                (Customer.phone.ilike(f"%{args['search']}%"))
            )
        
        # Paginate results
        page = args.get('page', 1)
        per_page = args.get('per_page', 20)
        customers_page = query.paginate(page=page, per_page=per_page)
        
        # Prepare results
        customers = []
        for customer in customers_page.items:
            # Get orders from this seller
            order_count = Order.query.filter_by(
                customer_id=customer.id,
                seller_id=user_id
            ).count()
            
            # Calculate total spent
            total_spent = db.session.query(db.func.sum(Order.total_amount)).filter(
                Order.customer_id == customer.id,
                Order.seller_id == user_id,
                Order.payment_status == 'paid'
            ).scalar() or 0
            
            customers.append({
                'id': customer.id,
                'name': customer.name,
                'email': customer.email,
                'phone': customer.phone,
                'order_count': order_count,
                'total_spent': float(total_spent)
            })
        
        return {
            'customers': customers,
            'page': customers_page.page,
            'pages': customers_page.pages,
            'total': customers_page.total
        }

class CustomerResource(Resource):
    def get(self, customer_id):
        parser = reqparse.RequestParser()
        parser.add_argument('token', location='headers')
        args = parser.parse_args()
        
        # Validate token
        user_id = verify_token(args.get('token'))
        if not user_id:
            return {'message': 'Unauthorized'}, 401
        
        # Get customer
        customer = Customer.query.get_or_404(customer_id)
        
        # Check if customer has orders from this seller
        order_count = Order.query.filter_by(
            customer_id=customer_id,
            seller_id=user_id
        ).count()
        
        if order_count == 0:
            return {'message': 'Customer not found'}, 404
        
        # Calculate total spent
        total_spent = db.session.query(db.func.sum(Order.total_amount)).filter(
            Order.customer_id == customer_id,
            Order.seller_id == user_id,
            Order.payment_status == 'paid'
        ).scalar() or 0
        
        # Prepare response
        customer_data = {
            'id': customer.id,
            'name': customer.name,
            'email': customer.email,
            'phone': customer.phone,
            'address': customer.address,
            'city': customer.city,
            'state': customer.state,
            'postal_code': customer.postal_code,
            'country': customer.country,
            'notes': customer.notes,
            'created_at': customer.created_at.isoformat(),
            'order_count': order_count,
            'total_spent': float(total_spent)
        }
        
        return customer_data

class CustomerOrdersResource(Resource):
    def get(self, customer_id):
        parser = reqparse.RequestParser()
        parser.add_argument('page', type=int, default=1, location='args')
        parser.add_argument('per_page', type=int, default=10, location='args')
        parser.add_argument('token', location='headers')
        args = parser.parse_args()
        
        # Validate token
        user_id = verify_token(args.get('token'))
        if not user_id:
            return {'message': 'Unauthorized'}, 401
        
        # Get customer
        customer = Customer.query.get_or_404(customer_id)
        
        # Get orders for this customer from this seller
        query = Order.query.filter_by(
            customer_id=customer_id,
            seller_id=user_id
        ).order_by(Order.created_at.desc())
        
        # Paginate results
        page = args.get('page', 1)
        per_page = args.get('per_page', 10)
        orders_page = query.paginate(page=page, per_page=per_page)
        
        # Prepare results
        orders = []
        for order in orders_page.items:
            orders.append({
                'id': order.id,
                'order_number': order.order_number,
                'status': order.status,
                'total_amount': order.total_amount,
                'payment_status': order.payment_status,
                'created_at': order.created_at.isoformat()
            })
        
        return {
            'orders': orders,
            'page': orders_page.page,
            'pages': orders_page.pages,
            'total': orders_page.total
        }

# Shipping Resources
class ShippingMethodListResource(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('token', location='headers')
        args = parser.parse_args()
        
        # Validate token
        user_id = verify_token(args.get('token'))
        if not user_id:
            return {'message': 'Unauthorized'}, 401
        
        # Get all shipping methods
        shipping_methods = ShippingMethod.query.all()
        
        # Prepare response
        methods = []
        for method in shipping_methods:
            methods.append({
                'id': method.id,
                'name': method.name,
                'description': method.description,
                'price': method.price,
                'estimated_days': method.estimated_days,
                'is_active': method.is_active
            })
        
        return {'shipping_methods': methods}
    
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('name', required=True, help='Name is required')
        parser.add_argument('description')
        parser.add_argument('price', type=float, required=True, help='Price is required')
        parser.add_argument('estimated_days')
        parser.add_argument('is_active', type=bool, default=True)
        parser.add_argument('token', location='headers')
        args = parser.parse_args()
        
        # Validate token
        user_id = verify_token(args.get('token'))
        if not user_id:
            return {'message': 'Unauthorized'}, 401
        
        # Create new shipping method
        shipping_method = ShippingMethod(
            name=args['name'],
            description=args.get('description'),
            price=args['price'],
            estimated_days=args.get('estimated_days'),
            is_active=args.get('is_active', True)
        )
        
        db.session.add(shipping_method)
        db.session.commit()
        
        return {'id': shipping_method.id, 'message': 'Shipping method created successfully'}

class ShippingZoneListResource(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('token', location='headers')
        args = parser.parse_args()
        
        # Validate token
        user_id = verify_token(args.get('token'))
        if not user_id:
            return {'message': 'Unauthorized'}, 401
        
        # Get all shipping zones
        shipping_zones = ShippingZone.query.all()
        
        # Prepare response
        zones = []
        for zone in shipping_zones:
            zones.append({
                'id': zone.id,
                'name': zone.name,
                'regions': zone.regions,
                'rate': zone.rate,
                'shipping_method_id': zone.shipping_method_id
            })
        
        return {'shipping_zones': zones}

# Promotion Resources
class PromotionListResource(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('token', location='headers')
        args = parser.parse_args()
        
        # Validate token
        user_id = verify_token(args.get('token'))
        if not user_id:
            return {'message': 'Unauthorized'}, 401
        
        # Get all promotions
        promotions = Promotion.query.all()
        
        # Prepare response
        promos = []
        for promo in promotions:
            promos.append({
                'id': promo.id,
                'name': promo.name,
                'description': promo.description,
                'code': promo.code,
                'discount_type': promo.discount_type,
                'discount_value': promo.discount_value,
                'start_date': promo.start_date.isoformat() if promo.start_date else None,
                'end_date': promo.end_date.isoformat() if promo.end_date else None,
                'is_active': promo.is_active,
                'usage_count': promo.usage_count,
                'usage_limit': promo.usage_limit,
                'minimum_order_amount': promo.minimum_order_amount
            })
        
        return {'promotions': promos}
    
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('name', required=True, help='Name is required')
        parser.add_argument('description')
        parser.add_argument('code')
        parser.add_argument('discount_type', required=True, help='Discount type is required')
        parser.add_argument('discount_value', type=float, required=True, help='Discount value is required')
        parser.add_argument('start_date')
        parser.add_argument('end_date')
        parser.add_argument('is_active', type=bool, default=True)
        parser.add_argument('usage_limit', type=int)
        parser.add_argument('minimum_order_amount', type=float)
        parser.add_argument('token', location='headers')
        args = parser.parse_args()
        
        # Validate token
        user_id = verify_token(args.get('token'))
        if not user_id:
            return {'message': 'Unauthorized'}, 401
        
        # Validate discount type
        if args['discount_type'] not in ['percentage', 'fixed']:
            return {'message': 'Invalid discount type'}, 400
        
        # Create new promotion
        promotion = Promotion(
            name=args['name'],
            description=args.get('description'),
            code=args.get('code'),
            discount_type=args['discount_type'],
            discount_value=args['discount_value'],
            start_date=datetime.fromisoformat(args['start_date']) if args.get('start_date') else None,
            end_date=datetime.fromisoformat(args['end_date']) if args.get('end_date') else None,
            is_active=args.get('is_active', True),
            usage_limit=args.get('usage_limit'),
            minimum_order_amount=args.get('minimum_order_amount')
        )
        
        db.session.add(promotion)
        db.session.commit()
        
        return {'id': promotion.id, 'message': 'Promotion created successfully'}

class PromotionResource(Resource):
    def get(self, promotion_id):
        parser = reqparse.RequestParser()
        parser.add_argument('token', location='headers')
        args = parser.parse_args()
        
        # Validate token
        user_id = verify_token(args.get('token'))
        if not user_id:
            return {'message': 'Unauthorized'}, 401
        
        # Get promotion
        promotion = Promotion.query.get_or_404(promotion_id)
        
        # Prepare response
        promo_data = {
            'id': promotion.id,
            'name': promotion.name,
            'description': promotion.description,
            'code': promotion.code,
            'discount_type': promotion.discount_type,
            'discount_value': promotion.discount_value,
            'start_date': promotion.start_date.isoformat() if promotion.start_date else None,
            'end_date': promotion.end_date.isoformat() if promotion.end_date else None,
            'is_active': promotion.is_active,
            'usage_count': promotion.usage_count,
            'usage_limit': promotion.usage_limit,
            'minimum_order_amount': promotion.minimum_order_amount
        }
        
        return promo_data
    
    def put(self, promotion_id):
        parser = reqparse.RequestParser()
        parser.add_argument('name')
        parser.add_argument('description')
        parser.add_argument('code')
        parser.add_argument('discount_type')
        parser.add_argument('discount_value', type=float)
        parser.add_argument('start_date')
        parser.add_argument('end_date')
        parser.add_argument('is_active', type=bool)
        parser.add_argument('usage_limit', type=int)
        parser.add_argument('minimum_order_amount', type=float)
        parser.add_argument('token', location='headers')
        args = parser.parse_args()
        
        # Validate token
        user_id = verify_token(args.get('token'))
        if not user_id:
            return {'message': 'Unauthorized'}, 401
        
        # Get promotion
        promotion = Promotion.query.get_or_404(promotion_id)
        
        # Update fields if provided
        for key, value in args.items():
            if key == 'token':
                continue
            elif key in ['start_date', 'end_date'] and value:
                setattr(promotion, key, datetime.fromisoformat(value))
            elif value is not None:
                setattr(promotion, key, value)
        
        db.session.commit()
        return {'message': 'Promotion updated successfully'}
    
    def delete(self, promotion_id):
        parser = reqparse.RequestParser()
        parser.add_argument('token', location='headers')
        args = parser.parse_args()
        
        # Validate token
        user_id = verify_token(args.get('token'))
        if not user_id:
            return {'message': 'Unauthorized'}, 401
        
        # Get promotion
        promotion = Promotion.query.get_or_404(promotion_id)
        
        db.session.delete(promotion)
        db.session.commit()
        
        return {'message': 'Promotion deleted successfully'}

# Notification Resources
class NotificationListResource(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('token', location='headers')
        args = parser.parse_args()
        
        # Validate token
        user_id = verify_token(args.get('token'))
        if not user_id:
            return {'message': 'Unauthorized'}, 401
        
        # Get notifications for the user
        notifications = Notification.query.filter_by(user_id=user_id).order_by(
            Notification.created_at.desc()
        ).all()
        
        # Prepare response
        notifs = []
        for notif in notifications:
            notifs.append({
                'id': notif.id,
                'title': notif.title,
                'message': notif.message,
                'type': notif.type,
                'is_read': notif.is_read,
                'created_at': notif.created_at.isoformat()
            })
        
        return {'notifications': notifs}

class NotificationResource(Resource):
    def put(self, notification_id):
        parser = reqparse.RequestParser()
        parser.add_argument('token', location='headers')
        args = parser.parse_args()
        
        # Validate token
        user_id = verify_token(args.get('token'))
        if not user_id:
            return {'message': 'Unauthorized'}, 401
        
        # Get notification
        notification = Notification.query.filter_by(
            id=notification_id,
            user_id=user_id
        ).first_or_404()
        
        # Mark as read
        notification.is_read = True
        db.session.commit()
        
        return {'message': 'Notification marked as read'}

class NotificationSettingsResource(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('token', location='headers')
        args = parser.parse_args()
        
        # Validate token
        user_id = verify_token(args.get('token'))
        if not user_id:
            return {'message': 'Unauthorized'}, 401
        
        # Get notification settings
        settings = {}
        for setting in Setting.query.filter_by(user_id=user_id).all():
            if setting.key.startswith('notify_'):
                settings[setting.key] = setting.value == 'true'
        
        # Default settings if none exist
        if not settings:
            settings = {
                'notify_new_order': True,
                'notify_order_status': True,
                'notify_low_stock': True,
                'notify_customer_message': True,
                'notify_email': True,
                'notify_app': True
            }
        
        return settings
    
    def put(self):
        parser = reqparse.RequestParser()
        parser.add_argument('notify_new_order', type=bool)
        parser.add_argument('notify_order_status', type=bool)
        parser.add_argument('notify_low_stock', type=bool)
        parser.add_argument('notify_customer_message', type=bool)
        parser.add_argument('notify_email', type=bool)
        parser.add_argument('notify_app', type=bool)
        parser.add_argument('token', location='headers')
        args = parser.parse_args()
        
        # Validate token
        user_id = verify_token(args.get('token'))
        if not user_id:
            return {'message': 'Unauthorized'}, 401
        
        # Update settings
        for key, value in args.items():
            if key != 'token' and value is not None and key.startswith('notify_'):
                setting = Setting.query.filter_by(user_id=user_id, key=key).first()
                
                if not setting:
                    setting = Setting(user_id=user_id, key=key)
                
                setting.value = 'true' if value else 'false'
                db.session.add(setting)
        
        db.session.commit()
        return {'message': 'Notification settings updated'}
