from flask import Flask, render_template, request, redirect, url_for, session
from models import db, User, Product, Category, Cart, Order, OrderItem, Review, Shipment
from forms import SearchForm, CategoryFilterForm, AddToCartForm, UpdateCartForm, RemoveFromCartForm, RegisterForm, LoginForm, EditAccountForm, OrderForm, ReviewForm, CheckoutForm, UpdateInventoryForm, InventoryItemForm
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'secret_key'
db.init_app(app)

@app.route('/', methods=['GET', 'POST'])
def home():
    search_form = SearchForm()
    category_form = CategoryFilterForm()
    category_form.category.choices = [(0, 'All Categories')] + [
        (c.id, c.name) for c in Category.query.all()
    ]

    # Handle search or category filter
    query = Product.query
    if search_form.validate_on_submit():
        query = query.filter(Product.name.contains(search_form.query.data))
    elif category_form.validate_on_submit() and category_form.category.data:
        query = query.filter(Product.category_id == category_form.category.data)

    # Dynamic recommendations (e.g., top-selling)
    top_products = Product.query.order_by(Product.sales_count.desc()).limit(5).all()

    products = query.all()
    return render_template(
        'index.html',
        search_form=search_form,
        category_form=category_form,
        products=products,
        top_products=top_products,
        user=session.get('username', 'Guest')
    )

@app.route('/cart', methods=['GET', 'POST'])
def view_cart():
    
    if 'username' not in session:
        return redirect(url_for('login', username='Guest'))

    user = User.query.filter_by(username=session['username']).first()
    if not user:
        return redirect(url_for('home'))

    cart_items = Cart.query.filter_by(user_id=user.id).all()
    total = sum(item.product.price * item.quantity for item in cart_items)

    return render_template('cart.html', cart_items=cart_items, total=total, update_form=UpdateCartForm(), remove_form=RemoveFromCartForm(), order_form=OrderForm())

@app.route('/cart/add', methods=['POST'])
def add_to_cart():
    if 'username' not in session:
        return redirect(url_for('login', username='Guest'))

    user = User.query.filter_by(username=session['username']).first()
    if not user:
        return redirect(url_for('home'))

    form = AddToCartForm()
    if form.validate_on_submit():
        product = Product.query.get(form.product_id.data)
        if product:
            cart_item = Cart.query.filter_by(user_id=user.id, product_id=product.id).first()
            if cart_item:
                cart_item.quantity += form.quantity.data
            else:
                cart_item = Cart(user_id=user.id, product_id=product.id, quantity=form.quantity.data)
                db.session.add(cart_item)
            db.session.commit()
    return redirect(url_for('view_cart'))

@app.route('/cart/update', methods=['POST'])
def update_cart():
    if 'username' not in session:
        return redirect(url_for('login', username='Guest'))

    user = User.query.filter_by(username=session['username']).first()
    if not user:
        return redirect(url_for('home'))

    form = UpdateCartForm()
    
    if form.validate_on_submit():
        cart_item = Cart.query.filter_by(user_id=user.id, product_id=request.form.get('product_id')).first()
        if cart_item:
            cart_item.quantity = form.quantity.data
            db.session.commit()
    return redirect(url_for('view_cart'))

@app.route('/cart/remove', methods=['POST'])
def remove_from_cart():
    if 'username' not in session:
        return redirect(url_for('login', username='Guest'))

    user = User.query.filter_by(username=session['username']).first()
    if not user:
        return redirect(url_for('home'))

    form = RemoveFromCartForm()
    if form.validate_on_submit():
        cart_item = Cart.query.filter_by(user_id=user.id, product_id=form.product_id.data).first()
        if cart_item:
            db.session.delete(cart_item)
            db.session.commit()
    return redirect(url_for('view_cart'))

from flask import flash, session

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'username' in session:
        return redirect(url_for('home'))

    form = RegisterForm()
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first():
            flash('Email already registered.')
            return redirect(url_for('register'))
        
        user = User(username=form.username.data, email=form.email.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful! Please log in.')
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        return redirect(url_for('home'))

    form = LoginForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            session['username'] = user.username
            session['user_id'] = user.id
            session['is_admin'] = user.is_admin
            flash('Login successful!')
            return redirect(url_for('home'))
        else:
            flash('Invalid email or password.')

    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.')
    return redirect(url_for('home'))

@app.route('/profile', methods=['GET', 'POST'])
def edit_profile():
    if 'username' not in session:
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])
    form = EditAccountForm(obj=user)

    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        user.address = form.address.data
        if form.password.data:
            user.set_password(form.password.data)
        db.session.commit()
        flash('Profile updated successfully.')
        return redirect(url_for('home'))

    return render_template('profile.html', form=form)

@app.route('/order', methods=['POST'])
def place_order():
    if 'username' not in session:
        return redirect(url_for('login', username='Guest'))

    user = User.query.filter_by(username=session['username']).first()
    if not user:
        return redirect(url_for('home'))
    
    form = OrderForm()
    if form.validate_on_submit():
        cart_items = Cart.query.filter_by(user_id=user.id).all()
        if not cart_items:
            flash('Your cart is empty.')
            return redirect(url_for('view_cart'))

        total_price = sum(item.product.price * item.quantity for item in cart_items)
        order = Order(user_id=user.id, timestamp=datetime.now(), total_price=total_price)
        db.session.add(order)
        db.session.commit()

        for item in cart_items:
            order_item = OrderItem(order_id=order.id, product_id=item.product.id, quantity=item.quantity)
            db.session.add(order_item)
            db.session.delete(item)

        db.session.commit()
        flash('Order placed successfully!')
        return redirect(url_for('view_orders'))

    flash('Failed to place order.')
    return redirect(url_for('view_cart'))

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    form = CheckoutForm()
    cart_items = []
    total_price = 0
    taxes = 0
    shipping_cost = 0
    total_cost = 0

    customer_id = session.get('user_id')

    if form.validate_on_submit():
        payment_info = form.payment_info.data
        shipping_address = form.shipping_address.data
        shipping_method = form.shipping_method.data

        # Validate customer ID
        customer = User.query.get(customer_id)
        if not customer:
            flash('Invalid customer ID.', 'danger')
            return redirect(url_for('checkout'))

        # Calculate taxes and shipping
        cart_items = Cart.query.filter_by(user_id=customer_id).all()
        if not cart_items:
            flash('Your cart is empty.', 'danger')
            return redirect(url_for('checkout'))

        total_price = sum(item.product.price * item.quantity for item in cart_items)
        tax_rate = 0.07  # Example tax rate
        shipping_cost = 10 if shipping_method == 'standard' else 20  # Example shipping costs
        taxes = total_price * tax_rate
        total_cost = total_price + taxes + shipping_cost

        # Create order
        order = Order(user_id=customer_id, timestamp=datetime.utcnow(), total_price=total_cost)
        db.session.add(order)
        db.session.commit()

        # Create order items and shipments
        for item in cart_items:
            order_item = OrderItem(order_id=order.id, product_id=item.product.id, quantity=item.quantity)
            db.session.add(order_item)
            db.session.delete(item)

        shipment = Shipment(order_id=order.id, address=shipping_address, method=shipping_method, cost=shipping_cost)
        db.session.add(shipment)
        db.session.commit()

        flash('Order placed successfully!', 'success')
        return redirect(url_for('view_orders'))
    
    cart_items = Cart.query.filter_by(user_id=customer_id).all()
    total_price = sum(item.product.price * item.quantity for item in cart_items)
    tax_rate = 0.07  # Example tax rate
    shipping_cost = 10 if form.shipping_method.data == 'standard' else 20  # Example shipping costs
    taxes = total_price * tax_rate
    total_cost = total_price + taxes + shipping_cost

    return render_template('checkout.html', form=form, cart_items=cart_items, total_price=total_price, taxes=taxes, shipping_cost=shipping_cost, total_cost=total_cost)

@app.route('/orders')
def view_orders():
    if 'username' not in session:
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])
    orders = user.orders
    return render_template('orders.html', orders=orders)

@app.route('/product/<int:product_id>')
def view_product(product_id):
    product = Product.query.get_or_404(product_id)

    form = AddToCartForm()
    return render_template('product.html', product=product, form=form, review_form=ReviewForm())

@app.route('/review/add/<int:product_id>', methods=['POST'])
def add_review(product_id):
    if 'username' not in session:
        return redirect(url_for('login', username='Guest'))

    user = User.query.filter_by(username=session['username']).first()
    if not user:
        return redirect(url_for('home'))

    form = ReviewForm()
    if form.validate_on_submit():
        existing_review = Review.query.filter_by(user_id=user.id, product_id=product_id).first()
        user_bought_product = OrderItem.query.join(Order).filter(Order.user_id == user.id, OrderItem.product_id == product_id).first()
        if existing_review or not user_bought_product:
            flash('You have already reviewed this product or not purchased this product.')
            return redirect(url_for('view_product', product_id=product_id))

        review = Review(user_id=user.id, product_id=product_id, rating=form.rating.data, comment=form.comment.data)
        db.session.add(review)
        db.session.commit()
        flash('Review added successfully!')
    else:
        flash('Invalid form submission.')

    return redirect(url_for('view_product', product_id=product_id))

from flask import Flask, render_template, request, redirect, url_for, session, flash
from functools import wraps
from models import db, User, Product, Cart, Order, OrderItem, Review, Warehouse, Category
from forms import AddToCartForm, UpdateCartForm, RemoveFromCartForm, OrderForm, ReviewForm, ProductForm, WarehouseForm, OrderStatusForm
from datetime import datetime
import os
from werkzeug.utils import secure_filename

app.config['UPLOAD_FOLDER'] = 'static/images'

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('is_admin'):
            return redirect(url_for('login', username='Guest'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/admin')
@admin_required
def admin_dashboard():
    return render_template('admin/dashboard.html')

@app.route('/admin/customers')
@admin_required
def admin_customers():
    customers = User.query.all()
    return render_template('admin/customers.html', customers=customers)

@app.route('/admin/add_customer', methods=['GET', 'POST'])
@admin_required
def admin_add_customer():
    form = RegisterForm()
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first():
            flash('Email already registered.')
            return redirect(url_for('admin_customers'))

        user = User(username=form.username.data, email=form.email.data, password=form.password.data, is_admin=form.is_admin.data)
        db.session.add(user)
        db.session.commit()
        flash('Customer added succesfuly')
        return redirect(url_for('admin_customers'))
    
    return render_template('admin/add_customer.html', form=form)

@app.route('/admin/update_customer', methods=['GET', 'POST'])
@admin_required
def admin_update_customer():
    customers = User.query.all()
    selected_customer_id = request.args.get('customer_id')
    selected_customer = None
    form = EditAccountForm()

    if selected_customer_id:
        selected_customer = User.query.get_or_404(selected_customer_id)
        form = EditAccountForm(obj=selected_customer)
        if form.validate_on_submit():
            selected_customer.username = form.username.data
            selected_customer.email = form.email.data
            selected_customer.address = form.address.data
            selected_customer.is_admin = form.is_admin.data
            if form.password.data:
                selected_customer.set_password(form.password.data)
            db.session.commit()
            flash('Customer updated successfully!')
            return redirect(url_for('admin_update_customer'))

    return render_template('admin/update_customer.html', customers=customers, form=form, selected_customer=selected_customer, selected_customer_id=selected_customer_id)

@app.route('/admin/sales_report')
@admin_required
def admin_sales_report():
    orders = Order.query.all()
    total_sales = sum(order.total_price for order in orders)
    return render_template('admin/sales_report.html', orders=orders, total_sales=total_sales)

@app.route('/admin/add_product', methods=['GET', 'POST'])
@admin_required
def admin_add_product():
    form = ProductForm()
    form.category_id.choices = [(c.id, c.name) for c in Category.query.all()]
    form.warehouse_id.choices = [(w.id, w.name) for w in Warehouse.query.all()]
    if form.validate_on_submit():
        filename = None
        if form.image.data:
            filename = secure_filename(form.image.data.filename)
            form.image.data.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        product = Product(name=form.name.data, price=form.price.data, category_id=form.category_id.data, warehouse_id=form.warehouse_id.data, image=filename)
        db.session.add(product)
        db.session.commit()
        flash('Product added successfully!')
        return redirect(url_for('admin_dashboard'))
    return render_template('admin/add_product.html', form=form)

@app.route('/admin/update_product/<int:product_id>', methods=['GET', 'POST'])
@admin_required
def admin_update_product(product_id):
    product = Product.query.get_or_404(product_id)
    form = ProductForm(obj=product)
    form.category_id.choices = [(c.id, c.name) for c in Category.query.all()]
    form.warehouse_id.choices = [(w.id, w.name) for w in Warehouse.query.all()]
    if form.validate_on_submit():
        if form.image.data:
            filename = secure_filename(form.image.data.filename)
            form.image.data.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            product.image = filename
        product.name = form.name.data
        product.price = form.price.data
        product.category_id = form.category_id.data
        product.warehouse_id = form.warehouse_id.data
        db.session.commit()
        flash('Product updated successfully!')
        return redirect(url_for('admin_dashboard'))
    return render_template('admin/update_product.html', form=form, product=product)

@app.route('/admin/delete_product/<int:product_id>', methods=['GET','POST'])
@admin_required
def admin_delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    flash('Product deleted successfully!')
    return redirect(url_for('home'))

@app.route('/admin/update_order/<int:order_id>', methods=['GET', 'POST'])
@admin_required
def admin_update_order(order_id):
    order = Order.query.get_or_404(order_id)
    form = OrderStatusForm(obj=order)
    if form.validate_on_submit():
        order.status = form.status.data
        db.session.commit()
        flash('Order status updated successfully!')
        return redirect(url_for('admin_dashboard'))
    return render_template('admin/update_order.html', form=form, order=order)

@app.route('/admin/add_warehouse', methods=['GET', 'POST'])
@admin_required
def admin_add_warehouse():
    form = WarehouseForm()
    if form.validate_on_submit():
        warehouse = Warehouse(name=form.name.data, address=form.address.data)
        db.session.add(warehouse)
        db.session.commit()
        flash('Warehouse added successfully!')
        return redirect(url_for('admin_dashboard'))
    return render_template('admin/add_warehouse.html', form=form)

@app.route('/admin/update_warehouse', methods=['GET', 'POST'])
@admin_required
def admin_update_warehouse():
    warehouses = Warehouse.query.all()
    selected_warehouse_id = request.args.get('warehouse_id')
    selected_warehouse = None
    form = WarehouseForm()

    if selected_warehouse_id:
        selected_warehouse = Warehouse.query.get_or_404(selected_warehouse_id)
        form = WarehouseForm(obj=selected_warehouse)
        if form.validate_on_submit():
            selected_warehouse.name = form.name.data
            selected_warehouse.address = form.address.data
            db.session.commit()
            flash('Warehouse updated successfully!')
            return redirect(url_for('admin_update_warehouse'))

    return render_template('admin/update_warehouse.html', warehouses=warehouses, form=form, selected_warehouse=selected_warehouse, selected_warehouse_id=selected_warehouse_id)

import subprocess

@app.route('/admin/restore_database', methods=['POST'])
@admin_required
def restore_database():
    try:
        subprocess.run(['python', 'restoreDatabase.py'], check=True)
        flash('Database restored successfully!', 'success')
    except subprocess.CalledProcessError as e:
        flash(f'Error restoring database: {e}', 'danger')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/update_inventory', methods=['GET', 'POST'])
@admin_required
def admin_update_inventory():
    warehouses = Warehouse.query.all()
    selected_warehouse_id = request.args.get('warehouse_id')
    selected_warehouse = None
    form = UpdateInventoryForm()

    if selected_warehouse_id:
        selected_warehouse = Warehouse.query.get_or_404(selected_warehouse_id)
        products = Product.query.filter_by(warehouse_id=selected_warehouse_id).all()
        print(form.items.data)
        if request.method == 'GET':
            for product in products:
                form.items.append_entry({'product_id': product.id, 'inventory': product.inventory})
    
        elif form.validate():
            for item in form.items.data:
                product = Product.query.get(item['product_id'])
                print(product)
                product.inventory = item['inventory']
            db.session.commit()
            flash('Inventory updated successfully!')
            return redirect(url_for('admin_update_inventory', warehouse_id=selected_warehouse_id))
        else:
            print(form.errors)

    return render_template('admin/update_inventory.html', warehouses=warehouses, form=form, selected_warehouse=selected_warehouse, selected_warehouse_id=selected_warehouse_id)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)



