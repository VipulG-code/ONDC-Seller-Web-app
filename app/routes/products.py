import os
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app import db
from app.models.product import Product, ProductVariant, ProductImage, Category
from app.forms.product import ProductForm, CategoryForm

products_bp = Blueprint('products', __name__, url_prefix='/products')

@products_bp.route('/')
@login_required
def list():
    """Display list of products with search and filters."""
    # Get query parameters for filtering
    search = request.args.get('search', '')
    category_id = request.args.get('category', type=int)
    status = request.args.get('status', '')
    sort = request.args.get('sort', 'name')
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    # Base query for products owned by current user
    query = Product.query.filter_by(seller_id=current_user.id)
    
    # Apply filters
    if search:
        query = query.filter(
            (Product.name.ilike(f'%{search}%')) | 
            (Product.sku.ilike(f'%{search}%'))
        )
    
    if category_id:
        query = query.filter_by(category_id=category_id)
    
    if status:
        query = query.filter_by(status=status)
    
    # Apply sorting
    if sort == 'name':
        query = query.order_by(Product.name)
    elif sort == 'price':
        query = query.order_by(Product.price)
    elif sort == 'stock':
        query = query.order_by(Product.stock_quantity)
    elif sort == 'created':
        query = query.order_by(Product.created_at.desc())
    else:
        query = query.order_by(Product.name)
    
    # Paginate results
    products = query.paginate(page=page, per_page=per_page)
    
    # Get all categories for filter dropdown
    categories = Category.query.all()
    
    return render_template('products/list.html', 
                          title='Products',
                          products=products,
                          categories=categories,
                          search=search,
                          category_id=category_id,
                          status=status,
                          sort=sort)

@products_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    """Add a new product."""
    form = ProductForm()
    form.category_id.choices = [(c.id, c.name) for c in Category.query.all()]
    
    if form.validate_on_submit():
        product = Product(
            seller_id=current_user.id,
            name=form.name.data,
            sku=form.sku.data,
            description=form.description.data,
            short_description=form.short_description.data,
            price=form.price.data,
            mrp=form.mrp.data,
            cost_price=form.cost_price.data,
            tax_rate=form.tax_rate.data,
            stock_quantity=form.stock_quantity.data,
            low_stock_threshold=form.low_stock_threshold.data,
            weight=form.weight.data,
            length=form.length.data,
            width=form.width.data,
            height=form.height.data,
            status=form.status.data,
            featured=form.featured.data,
            category_id=form.category_id.data,
            hsn_code=form.hsn_code.data,
            ondc_category=form.ondc_category.data
        )
        
        db.session.add(product)
        db.session.commit()
        
        # Handle image uploads
        if form.images.data:
            for image_file in form.images.data:
                if image_file:
                    filename = secure_filename(image_file.filename)
                    image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                    image_file.save(image_path)
                    
                    # Create image record
                    image = ProductImage(
                        product_id=product.id,
                        image_path=os.path.join('uploads', filename),
                        alt_text=product.name,
                        is_primary=True if product.images.count() == 0 else False
                    )
                    db.session.add(image)
            
            db.session.commit()
        
        flash('Product added successfully!', 'success')
        return redirect(url_for('products.list'))
    
    return render_template('products/edit.html', 
                          title='Add Product',
                          form=form,
                          product=None)

@products_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    """Edit an existing product."""
    product = Product.query.filter_by(id=id, seller_id=current_user.id).first_or_404()
    
    form = ProductForm(obj=product)
    form.category_id.choices = [(c.id, c.name) for c in Category.query.all()]
    
    if form.validate_on_submit():
        # Update product fields
        product.name = form.name.data
        product.sku = form.sku.data
        product.description = form.description.data
        product.short_description = form.short_description.data
        product.price = form.price.data
        product.mrp = form.mrp.data
        product.cost_price = form.cost_price.data
        product.tax_rate = form.tax_rate.data
        product.stock_quantity = form.stock_quantity.data
        product.low_stock_threshold = form.low_stock_threshold.data
        product.weight = form.weight.data
        product.length = form.length.data
        product.width = form.width.data
        product.height = form.height.data
        product.status = form.status.data
        product.featured = form.featured.data
        product.category_id = form.category_id.data
        product.hsn_code = form.hsn_code.data
        product.ondc_category = form.ondc_category.data
        
        # Handle image uploads
        if form.images.data:
            for image_file in form.images.data:
                if image_file and image_file.filename:
                    filename = secure_filename(image_file.filename)
                    image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                    image_file.save(image_path)
                    
                    # Create image record
                    image = ProductImage(
                        product_id=product.id,
                        image_path=os.path.join('uploads', filename),
                        alt_text=product.name,
                        is_primary=True if product.images.count() == 0 else False
                    )
                    db.session.add(image)
        
        db.session.commit()
        flash('Product updated successfully!', 'success')
        return redirect(url_for('products.list'))
    
    return render_template('products/edit.html', 
                          title='Edit Product',
                          form=form,
                          product=product)

@products_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    """Delete a product."""
    product = Product.query.filter_by(id=id, seller_id=current_user.id).first_or_404()
    
    db.session.delete(product)
    db.session.commit()
    
    flash('Product deleted successfully!', 'success')
    return redirect(url_for('products.list'))

@products_bp.route('/categories')
@login_required
def categories():
    """Manage product categories."""
    categories = Category.query.all()
    form = CategoryForm()
    
    return render_template('products/categories.html',
                          title='Categories',
                          categories=categories,
                          form=form)

@products_bp.route('/categories/add', methods=['POST'])
@login_required
def add_category():
    """Add a new category."""
    form = CategoryForm()
    
    if form.validate_on_submit():
        category = Category(
            name=form.name.data,
            description=form.description.data,
            parent_id=form.parent_id.data if form.parent_id.data else None
        )
        
        db.session.add(category)
        db.session.commit()
        
        flash('Category added successfully!', 'success')
    
    return redirect(url_for('products.categories'))

@products_bp.route('/categories/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_category(id):
    """Edit an existing category."""
    category = Category.query.get_or_404(id)
    
    if request.method == 'POST':
        form = CategoryForm(request.form)
        
        if form.validate():
            category.name = form.name.data
            category.description = form.description.data
            category.parent_id = form.parent_id.data if form.parent_id.data else None
            
            db.session.commit()
            flash('Category updated successfully!', 'success')
            return redirect(url_for('products.categories'))
    else:
        form = CategoryForm(obj=category)
    
    form.parent_id.choices = [(c.id, c.name) for c in Category.query.filter(Category.id != id).all()]
    form.parent_id.choices.insert(0, (0, 'None'))
    
    return render_template('products/edit_category.html',
                          title='Edit Category',
                          form=form,
                          category=category)

@products_bp.route('/categories/delete/<int:id>', methods=['POST'])
@login_required
def delete_category(id):
    """Delete a category."""
    category = Category.query.get_or_404(id)
    
    # Check if there are products using this category
    if Product.query.filter_by(category_id=id).count() > 0:
        flash('Cannot delete category with associated products.', 'danger')
        return redirect(url_for('products.categories'))
    
    db.session.delete(category)
    db.session.commit()
    
    flash('Category deleted successfully!', 'success')
    return redirect(url_for('products.categories'))
