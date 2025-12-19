from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, g
from flask_login import login_user, logout_user, current_user, login_required
from urllib.parse import urlsplit
from app import db
from app.forms import LoginForm, RegistrationForm, RequestForm, BuyCreditsForm, BidForm
from app.models import User, Request, Bid, CreditTransaction, SiteSetting, Ticker
from flask import current_app as app

# We need to register routes. Since I didn't use blueprints, I will define a function or just import app?
# Ah, I see in __init__.py I return app. 
# The standard pattern without blueprints is:
# app = Flask(__name__)
# from app import routes
# But I used a factory.
# If I use a factory, I MUST use Blueprints for routes, OR push context.
# Let's switch to using a Blueprint for the main routes to be clean.

from flask import Blueprint
bp = Blueprint('main', __name__)

@bp.before_request
def before_request():
    g.site_setting = SiteSetting.query.first()
    g.tickers = Ticker.query.all()

@bp.route('/')
@bp.route('/index')
def index():
    return render_template('index.html', title='Home')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(db.select(User).where(User.username == form.username.data))
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('main.login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('main.index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, 
                    is_seller=form.is_seller.data, is_buyer=True,
                    tax_id=form.tax_id.data) # Default everyone is buyer
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('main.login'))
    return render_template('register.html', title='Register', form=form)

@bp.route('/buy_credits', methods=['GET', 'POST'])
@login_required
def buy_credits():
    form = BuyCreditsForm()
    if form.validate_on_submit():
        package = form.package.data
        credits_to_add = 0
        cost = 0
        if package == '10':
            credits_to_add = 10
            cost = 100
        elif package == '20':
            credits_to_add = 20
            cost = 170
        elif package == '50':
            credits_to_add = 50
            cost = 350
        
        if credits_to_add > 0:
            current_user.credits += credits_to_add
            transaction = CreditTransaction(user_id=current_user.id, amount=credits_to_add, description=f"Bought {package} credits package")
            db.session.add(transaction)
            db.session.commit()
            flash(f'Successfully purchased {credits_to_add} credits!')
            return redirect(url_for('main.dashboard'))
            
    return render_template('buy_credits.html', title='Buy Credits', form=form)

@bp.route('/dashboard')
@login_required
def dashboard():
    my_requests = current_user.requests.order_by(Request.timestamp.desc()).all()
    my_bids = current_user.bids.order_by(Bid.timestamp.desc()).all()
    return render_template('dashboard.html', title='Dashboard', my_requests=my_requests, my_bids=my_bids)

@bp.route('/create_request', methods=['GET', 'POST'])
@login_required
def create_request():
    if current_user.credits < 1:
        flash('You need at least 1 credit to create a request.')
        return redirect(url_for('main.buy_credits'))
        
    form = RequestForm()
    if form.validate_on_submit():
        req = Request(
            user_id=current_user.id,
            category=form.category.data,
            sub_category=form.sub_category.data,
            product_type=form.product_type.data,
            spec=form.spec.data,
            origin=form.origin.data,
            application=form.application.data,
            quantity=form.quantity.data,
            product_status=form.product_status.data,
            customs_status=form.customs_status.data,
            packaging=form.packaging.data,
            deadline=datetime.combine(form.deadline.data, datetime.min.time()) if form.deadline.data else None,
            status='Open'
        )
        current_user.credits -= 1
        db.session.add(req)
        db.session.commit()
        flash('Request created successfully! 1 Credit deducted.')
        return redirect(url_for('main.dashboard'))
        
    return render_template('create_request.html', title='Create Request', form=form)

@bp.route('/marketplace')
@login_required
def marketplace():
    # Show all requests not by current user
    requests = Request.query.filter(Request.user_id != current_user.id).order_by(Request.timestamp.desc()).all()
    return render_template('marketplace.html', title='Marketplace', requests=requests)

@bp.route('/request/<int:id>', methods=['GET', 'POST'])
@login_required
def request_detail(id):
    req = db.session.get(Request, id)
    if not req:
        flash('Request not found.')
        return redirect(url_for('main.marketplace'))
    
    # Handle Bid Submission
    if request.method == 'POST':
        if not current_user.is_seller:
            flash('Only sellers can submit bids.')
            return redirect(url_for('main.request_detail', id=id))
            
        price = request.form.get('price')
        details = request.form.get('details') # e.g. "1100 USD / Ton + KDV"
        
        bid = Bid(request_id=id, seller_id=current_user.id, price=price, details=details)
        db.session.add(bid)
        db.session.commit()
        flash('Bid submitted successfully.')
        return redirect(url_for('main.request_detail', id=id))
        
    return render_template('request_detail.html', title='Request Detail', req=req)
