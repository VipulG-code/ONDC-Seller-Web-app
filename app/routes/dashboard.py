from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.models.order import Order
from app.models.product import Product
from app.utils.helpers import get_sales_data, get_recent_orders, get_low_stock_products

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@login_required
def index():
    """Dashboard homepage with key metrics and charts."""
    # Get sales summary data for charts
    daily_sales, weekly_sales, monthly_sales = get_sales_data(current_user.id)
    
    # Get recent orders
    recent_orders = get_recent_orders(current_user.id, limit=5)
    
    # Get low stock products
    low_stock_products = get_low_stock_products(current_user.id)
    
    # Get order statistics
    total_orders = Order.query.filter_by(seller_id=current_user.id).count()
    pending_orders = Order.query.filter_by(seller_id=current_user.id, status='new').count()
    processing_orders = Order.query.filter_by(seller_id=current_user.id, status='processing').count()
    
    # Get product statistics
    total_products = Product.query.filter_by(seller_id=current_user.id).count()
    active_products = Product.query.filter_by(seller_id=current_user.id, status='active').count()
    
    return render_template('dashboard/index.html',
                          title='Dashboard',
                          daily_sales=daily_sales,
                          weekly_sales=weekly_sales,
                          monthly_sales=monthly_sales,
                          recent_orders=recent_orders,
                          low_stock_products=low_stock_products,
                          total_orders=total_orders,
                          pending_orders=pending_orders,
                          processing_orders=processing_orders,
                          total_products=total_products,
                          active_products=active_products)
