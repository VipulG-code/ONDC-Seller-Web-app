from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models.customer import Customer
from app.models.order import Order
from app.forms.customer import CustomerForm

customers_bp = Blueprint('customers', __name__, url_prefix='/customers')

@customers_bp.route('/')
@login_required
def list():
    """Display list of customers with search and filters."""
    # Get query parameters for filtering
    search = request.args.get('search', '')
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # Base query for customers with orders from the current seller
    query = Customer.query.join(Order).filter(Order.seller_id == current_user.id).distinct()
    
    # Apply search filter if provided
    if search:
        query = query.filter(
            (Customer.name.ilike(f'%{search}%')) | 
            (Customer.email.ilike(f'%{search}%')) |
            (Customer.phone.ilike(f'%{search}%'))
        )
    
    # Order by name
    query = query.order_by(Customer.name)
    
    # Paginate results
    customers = query.paginate(page=page, per_page=per_page)
    
    return render_template('customers/list.html',
                          title='Customers',
                          customers=customers,
                          search=search)

@customers_bp.route('/<int:id>')
@login_required
def detail(id):
    """Display detailed information about a customer."""
    # Get the customer
    customer = Customer.query.get_or_404(id)
    
    # Get orders for this customer from the current seller
    orders = Order.query.filter_by(
        customer_id=id,
        seller_id=current_user.id
    ).order_by(Order.created_at.desc()).all()
    
    # Calculate total spent
    total_spent = sum(order.total_amount for order in orders if order.payment_status == 'paid')
    
    return render_template('customers/detail.html',
                          title=f'Customer: {customer.name}',
                          customer=customer,
                          orders=orders,
                          total_spent=total_spent,
                          order_count=len(orders))

@customers_bp.route('/<int:id>/add-note', methods=['POST'])
@login_required
def add_note(id):
    """Add a note to a customer record."""
    customer = Customer.query.get_or_404(id)
    
    # Verify this customer has orders from the current seller
    order_count = Order.query.filter_by(customer_id=id, seller_id=current_user.id).count()
    if order_count == 0:
        flash('You do not have permission to modify this customer', 'danger')
        return redirect(url_for('customers.list'))
    
    note = request.form.get('note')
    if note:
        if customer.notes:
            customer.notes = f"{customer.notes}\n\n{note}"
        else:
            customer.notes = note
            
        db.session.commit()
        flash('Note added successfully', 'success')
    else:
        flash('Note cannot be empty', 'danger')
    
    return redirect(url_for('customers.detail', id=id))


@customers_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    """Add a new customer."""
    form = CustomerForm()
    if form.validate_on_submit():
        customer = Customer()
        form.populate_obj(customer)
        db.session.add(customer)
        db.session.commit()
        flash('Customer added successfully', 'success')
        return redirect(url_for('customers.detail', id=customer.id))
    return render_template('customers/form.html', form=form, title='Add Customer')

@customers_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    """Edit a customer."""
    customer = Customer.query.get_or_404(id)
    form = CustomerForm(obj=customer)
    if form.validate_on_submit():
        form.populate_obj(customer)
        db.session.commit()
        flash('Customer updated successfully', 'success')
        return redirect(url_for('customers.detail', id=id))
    return render_template('customers/form.html', form=form, customer=customer, title='Edit Customer')

@customers_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    """Delete a customer."""
    customer = Customer.query.get_or_404(id)
    db.session.delete(customer)
    db.session.commit()
    flash('Customer deleted successfully', 'success')
    return redirect(url_for('customers.list'))
