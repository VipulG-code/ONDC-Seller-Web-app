from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.order import Order, OrderItem
from app.models.customer import Customer
from app.utils.helpers import generate_invoice_pdf

orders_bp = Blueprint('orders', __name__, url_prefix='/orders')

@orders_bp.route('/')
@login_required
def list():
    """Display list of orders with filters."""
    # Get query parameters for filtering
    status = request.args.get('status', '')
    search = request.args.get('search', '')
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # Base query for orders belonging to current user
    query = Order.query.filter_by(seller_id=current_user.id)
    
    # Apply filters
    if status:
        query = query.filter_by(status=status)
    
    if search:
        query = query.filter(
            (Order.order_number.ilike(f'%{search}%')) | 
            (Order.customer_name.ilike(f'%{search}%')) |
            (Order.customer_email.ilike(f'%{search}%'))
        )
    
    # Apply date filters if provided
    if date_from:
        query = query.filter(Order.created_at >= date_from)
    
    if date_to:
        query = query.filter(Order.created_at <= date_to)
    
    # Order by most recent first
    query = query.order_by(Order.created_at.desc())
    
    # Paginate results
    orders = query.paginate(page=page, per_page=per_page)
    
    return render_template('orders/list.html',
                          title='Orders',
                          orders=orders,
                          status=status,
                          search=search,
                          date_from=date_from,
                          date_to=date_to)

@orders_bp.route('/<int:id>')
@login_required
def detail(id):
    """Display detailed information about an order."""
    order = Order.query.filter_by(id=id, seller_id=current_user.id).first_or_404()
    
    return render_template('orders/detail.html',
                          title=f'Order #{order.order_number}',
                          order=order)

@orders_bp.route('/<int:id>/update-status', methods=['POST'])
@login_required
def update_status(id):
    """Update the status of an order."""
    order = Order.query.filter_by(id=id, seller_id=current_user.id).first_or_404()
    
    status = request.form.get('status')
    if status and status in ['new', 'processing', 'shipped', 'delivered', 'cancelled']:
        order.status = status
        db.session.commit()
        
        flash(f'Order status updated to {status}', 'success')
    else:
        flash('Invalid status', 'danger')
    
    return redirect(url_for('orders.detail', id=id))

@orders_bp.route('/<int:id>/add-note', methods=['POST'])
@login_required
def add_note(id):
    """Add a note to an order."""
    order = Order.query.filter_by(id=id, seller_id=current_user.id).first_or_404()
    
    note = request.form.get('note')
    if note:
        if order.notes:
            order.notes = f"{order.notes}\n\n{note}"
        else:
            order.notes = note
            
        db.session.commit()
        flash('Note added successfully', 'success')
    else:
        flash('Note cannot be empty', 'danger')
    
    return redirect(url_for('orders.detail', id=id))

@orders_bp.route('/<int:id>/invoice')
@login_required
def invoice(id):
    """Generate and download an invoice for an order."""
    order = Order.query.filter_by(id=id, seller_id=current_user.id).first_or_404()
    
    # Generate PDF invoice (in a real app, this would generate a PDF)
    # For this example, we'll just show the invoice in a template
    return render_template('orders/invoice.html',
                          title=f'Invoice #{order.order_number}',
                          order=order)

@orders_bp.route('/<int:id>/cancel', methods=['POST'])
@login_required
def cancel(id):
    """Cancel an order."""
    order = Order.query.filter_by(id=id, seller_id=current_user.id).first_or_404()
    
    if order.status in ['delivered', 'cancelled']:
        flash('Cannot cancel an order that is already delivered or cancelled', 'danger')
    else:
        order.status = 'cancelled'
        db.session.commit()
        
        flash('Order cancelled successfully', 'success')
    
    return redirect(url_for('orders.detail', id=id))

@orders_bp.route('/<int:id>/tracking', methods=['POST'])
@login_required
def update_tracking(id):
    """Update tracking information for an order."""
    order = Order.query.filter_by(id=id, seller_id=current_user.id).first_or_404()
    
    tracking_number = request.form.get('tracking_number')
    shipping_method = request.form.get('shipping_method')
    
    if tracking_number:
        order.tracking_number = tracking_number
    
    if shipping_method:
        order.shipping_method = shipping_method
    
    db.session.commit()
    flash('Tracking information updated', 'success')
    
    return redirect(url_for('orders.detail', id=id))
