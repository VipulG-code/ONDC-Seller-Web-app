import os
import random
from datetime import datetime, timedelta
from app import db
from app.models.order import Order
from app.models.product import Product

def get_sales_data(seller_id):
    """
    Get sales data for dashboard charts.
    
    Args:
        seller_id: ID of the current seller
        
    Returns:
        Tuple containing daily, weekly, and monthly sales data
    """
    # Get current date and time
    now = datetime.utcnow()
    
    # Calculate date ranges
    today = now.date()
    past_week = today - timedelta(days=7)
    past_month = today - timedelta(days=30)
    
    # Get daily sales (last 7 days)
    daily_sales = []
    for i in range(6, -1, -1):
        date = today - timedelta(days=i)
        date_str = date.strftime('%Y-%m-%d')
        
        # Get orders for this date
        daily_total = db.session.query(db.func.sum(Order.total_amount)).filter(
            Order.seller_id == seller_id,
            db.func.date(Order.created_at) == date,
            Order.status != 'cancelled'
        ).scalar() or 0
        
        daily_sales.append({
            'date': date.strftime('%a'),
            'amount': float(daily_total)
        })
    
    # Get weekly sales (last 4 weeks)
    weekly_sales = []
    for i in range(3, -1, -1):
        week_start = today - timedelta(days=today.weekday() + 7 * i)
        week_end = week_start + timedelta(days=6)
        week_str = f"{week_start.strftime('%d %b')} - {week_end.strftime('%d %b')}"
        
        # Get orders for this week
        weekly_total = db.session.query(db.func.sum(Order.total_amount)).filter(
            Order.seller_id == seller_id,
            db.func.date(Order.created_at) >= week_start,
            db.func.date(Order.created_at) <= week_end,
            Order.status != 'cancelled'
        ).scalar() or 0
        
        weekly_sales.append({
            'week': f"Week {4-i}",
            'amount': float(weekly_total)
        })
    
    # Get monthly sales (last 6 months)
    monthly_sales = []
    for i in range(5, -1, -1):
        month = now.month - i
        year = now.year
        
        # Adjust year if month is negative
        while month <= 0:
            month += 12
            year -= 1
        
        # Get orders for this month
        month_total = db.session.query(db.func.sum(Order.total_amount)).filter(
            Order.seller_id == seller_id,
            db.func.extract('month', Order.created_at) == month,
            db.func.extract('year', Order.created_at) == year,
            Order.status != 'cancelled'
        ).scalar() or 0
        
        # Get month name
        month_name = datetime(year, month, 1).strftime('%b')
        
        monthly_sales.append({
            'month': month_name,
            'amount': float(month_total)
        })
    
    return daily_sales, weekly_sales, monthly_sales

def get_recent_orders(seller_id, limit=5):
    """
    Get recent orders for the seller.
    
    Args:
        seller_id: ID of the current seller
        limit: Maximum number of orders to return
        
    Returns:
        List of recent Order objects
    """
    return Order.query.filter_by(seller_id=seller_id).order_by(
        Order.created_at.desc()
    ).limit(limit).all()

def get_low_stock_products(seller_id):
    """
    Get products with low stock.
    
    Args:
        seller_id: ID of the current seller
        
    Returns:
        List of Product objects with stock below threshold
    """
    return Product.query.filter(
        Product.seller_id == seller_id,
        Product.stock_quantity <= Product.low_stock_threshold
    ).order_by(Product.stock_quantity).all()

def generate_invoice_pdf(order):
    """
    Generate a PDF invoice for an order.
    
    Args:
        order: The Order object
        
    Returns:
        Path to the generated PDF file
    """
    # In a real application, this would generate a PDF using a library like ReportLab
    # For this example, we'll just return a placeholder value
    return f"invoice_{order.order_number}.pdf"

def generate_order_number():
    """
    Generate a unique order number.
    
    Returns:
        String: A unique order number
    """
    timestamp = datetime.utcnow().strftime('%Y%m%d%H%M')
    random_digits = str(random.randint(1000, 9999))
    return f"ORD-{timestamp}-{random_digits}"
