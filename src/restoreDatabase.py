from app import db, app
from models import User, Product, Category, Warehouse

with app.app_context():
    # Drop all tables
    db.drop_all()

    # Create all tables
    db.create_all()

    # Check if categories already exist
    electronics = Category.query.filter_by(name="Electronics").first()
    if not electronics:
        electronics = Category(name="Electronics")
        db.session.add(electronics)

    fashion = Category.query.filter_by(name="Fashion").first()
    if not fashion:
        fashion = Category(name="Fashion")
        db.session.add(fashion)

    db.session.commit()

    # Add warehouses
    warehouse1 = Warehouse(name="Warehouse 1", address="123 Warehouse St")
    warehouse2 = Warehouse(name="Warehouse 2", address="456 Warehouse Ave")
    db.session.add_all([warehouse1, warehouse2])
    db.session.commit()

    # Add products
    db.session.add_all([
        Product(name="Smartphone", price=699.99, image="smartphone.jpg", category_id=electronics.id, sales_count=50, warehouse_id=warehouse1.id, description="A very nice smartphone"),
        Product(name="Laptop", price=1299.99, image="laptop.jpg", category_id=electronics.id, sales_count=30, warehouse_id=warehouse1.id, description="A very nice laptop"),
        Product(name="T-Shirt", price=19.99, image="tshirt.jpg", category_id=fashion.id, sales_count=70, warehouse_id=warehouse2.id, description="A very nice t-shirt"),
    ])
    db.session.commit()

    # Add sample users
    user1 = User(username="testuser1", email="test1@example.com", password="hashed_password1", address="123 Main St")
    user2 = User(username="testuser2", email="test2@example.com", password="hashed_password2", address="456 Elm St")
    admin_user = User(username="admin", email="admin@admin", password="admin", address="789 Admin Blvd", is_admin=True)
    db.session.add_all([user1, user2, admin_user])
    db.session.commit()