from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db, login

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    credits = db.Column(db.Integer, default=0)
    is_seller = db.Column(db.Boolean, default=False)
    is_buyer = db.Column(db.Boolean, default=True)
    
    # Admin & CRM fields
    is_admin = db.Column(db.Boolean, default=False)
    is_blocked = db.Column(db.Boolean, default=False)
    tax_id = db.Column(db.String(20))
    is_verified = db.Column(db.Boolean, default=False)

    requests = db.relationship('Request', backref='author', lazy='dynamic')
    bids = db.relationship('Bid', backref='bidder', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))

class Request(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    category = db.Column(db.String(100))
    sub_category = db.Column(db.String(100))
    
    # Specific fields mentioned in prompt
    product_type = db.Column(db.String(100)) # Ürün Cinsi
    spec = db.Column(db.String(100))         # Ürün Spesifik Özelliği
    origin = db.Column(db.String(100))       # Menşei
    application = db.Column(db.String(100))  # Uygulama Alanı
    quantity = db.Column(db.String(50))      # Miktar
    product_status = db.Column(db.String(50)) # Ürün Durumu
    customs_status = db.Column(db.String(50)) # Gümrükleme Statüsü
    packaging = db.Column(db.String(50))      # Ambalaj Türü
    
    deadline = db.Column(db.DateTime)         # Deadline for the request
    status = db.Column(db.String(20), default='Open')
    details = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    
    bids = db.relationship('Bid', backref='request', lazy='dynamic')

class Bid(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer, db.ForeignKey('request.id'))
    seller_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    price = db.Column(db.String(50)) # Store as string to include currency or formatted "1100 USD"
    details = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

class CreditTransaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    amount = db.Column(db.Integer)
    description = db.Column(db.String(200))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True)
    # Storing schema as simple string/JSON for dynamic fields e.g., "Origin,MFI"
    schema = db.Column(db.Text) 
    
    sub_categories = db.relationship('Category', backref=db.backref('parent', remote_side=[id]), lazy='dynamic')

class SiteSetting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    logo_url = db.Column(db.String(255))
    contact_info = db.Column(db.String(255))
    seo_title = db.Column(db.String(255))
    announcement = db.Column(db.String(255))

class Ticker(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50)) # e.g. USD/TRY or PVC Price
    value = db.Column(db.String(50))
    change_rate = db.Column(db.String(20)) # e.g. "+0.5%"
