from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, FloatField, FileField, BooleanField, FieldList, FormField
from wtforms.validators import DataRequired

class SearchForm(FlaskForm):
    query = StringField('Search Products', validators=[DataRequired()])
    submit = SubmitField('Search')

class CategoryFilterForm(FlaskForm):
    category = SelectField('Category', coerce=int)
    submit = SubmitField('Filter')

from wtforms import IntegerField
from wtforms.validators import NumberRange

class AddToCartForm(FlaskForm):
    product_id = IntegerField('Product ID', validators=[DataRequired()])
    quantity = IntegerField('Quantity', validators=[DataRequired(), NumberRange(min=1)])
    submit = SubmitField('Add to Cart')

class UpdateCartForm(FlaskForm):
    product_id = IntegerField('Product ID', validators=[DataRequired()])
    quantity = IntegerField('Quantity', validators=[DataRequired(), NumberRange(min=1)])
    submit = SubmitField('Update')

class RemoveFromCartForm(FlaskForm):
    product_id = IntegerField('Product ID', validators=[DataRequired()])
    submit = SubmitField('Remove')

from wtforms import PasswordField, EmailField, TextAreaField
from wtforms.validators import EqualTo

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField('Confirm Password')
    is_admin = BooleanField('Admin')
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class EditAccountForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired()])
    address = TextAreaField('Address')
    password = PasswordField('New Password', validators=[EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField('Confirm New Password')
    is_admin = BooleanField('Admin')
    submit = SubmitField('Save Changes')

class OrderForm(FlaskForm):
    submit = SubmitField('CheckOut')

class ReviewForm(FlaskForm):
    rating = IntegerField('Rating', validators=[DataRequired(), NumberRange(min=1, max=5)])
    comment = TextAreaField('Comment', validators=[DataRequired()])
    submit = SubmitField('Submit Review')

class ProductForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    price = FloatField('Price', validators=[DataRequired(), NumberRange(min=0)])
    category_id = SelectField('Category', coerce=int, validators=[DataRequired()])
    warehouse_id = SelectField('Warehouse', coerce=int, validators=[DataRequired()])
    image = FileField('Product Image')
    submit = SubmitField('Save')

class WarehouseForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    address = StringField('Address', validators=[DataRequired()])
    submit = SubmitField('Save')

class OrderStatusForm(FlaskForm):
    status = SelectField('Status', choices=[('Pending', 'Pending'), ('Shipped', 'Shipped'), ('Delivered', 'Delivered')], validators=[DataRequired()])
    submit = SubmitField('Update Status')

class CheckoutForm(FlaskForm):
    payment_info = StringField('Payment Information', validators=[DataRequired()])
    shipping_address = StringField('Shipping Address', validators=[DataRequired()])
    shipping_method = SelectField('Shipping Method', choices=[('standard', 'Standard'), ('express', 'Express')], validators=[DataRequired()])
    submit = SubmitField('Checkout')

class InventoryItemForm(FlaskForm):
    product_id = IntegerField('Product ID')
    inventory = IntegerField('Inventory', validators=[NumberRange(min=0)])

class UpdateInventoryForm(FlaskForm):
    items = FieldList(FormField(InventoryItemForm))
    submit = SubmitField('Update Inventory')
