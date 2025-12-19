from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, DateField, IntegerField, TextAreaField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from app.models import User

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password_2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    tax_id = StringField('Tax ID (Vergi No)')
    is_seller = BooleanField('I want to sell')
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')
from app.models import Category

class RequestForm(FlaskForm):
    category = SelectField('Category', validators=[DataRequired()])
    sub_category = StringField('Sub Category') 
    
    def __init__(self, *args, **kwargs):
        super(RequestForm, self).__init__(*args, **kwargs)
        # Populate choices from DB
        # Note: This requires application context when form is instantiated
        try:
            cats = Category.query.filter(Category.parent_id == None).all()
            self.category.choices = [(c.name, c.name) for c in cats]
        except Exception:
            self.category.choices = []
    
    product_type = StringField('Product Type (Ürün Cinsi)', validators=[DataRequired()])
    spec = StringField('Specific Feature (Ürün Spesifik Özelliği)')
    origin = StringField('Origin (Menşei)')
    application = StringField('Application Area (Uygulama Alanı)')
    quantity = StringField('Quantity (Miktar)', validators=[DataRequired()])
    product_status = StringField('Product Status (Ürün Durumu)')
    customs_status = StringField('Customs Status (Gümrükleme Statüsü)')
    packaging = StringField('Packaging Type (Ambalaj Türü)')
    deadline = DateField('Deadline', format='%Y-%m-%d', validators=[DataRequired()])
    submit = SubmitField('Submit Request')

class BuyCreditsForm(FlaskForm):
    package = SelectField('Package', choices=[('10', '10 Credits ($100)'), ('20', '20 Credits ($170)'), ('50', '50 Credits ($350)')], validators=[DataRequired()])
    submit = SubmitField('Buy Now')

class BidForm(FlaskForm):
    price = StringField('Price (Fiyat)', validators=[DataRequired()])
    details = TextAreaField('Details / Notes')
    submit = SubmitField('Submit Offer')
