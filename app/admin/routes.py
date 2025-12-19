from flask import Blueprint, render_template, redirect, url_for, flash, request
from app import db
from app.models import User, Request, CreditTransaction, SiteSetting, Ticker, Category
from app.admin.utils import admin_required
from app.admin.forms import AddCategoryForm, AddTickerForm, SiteSettingsForm, AdminActionForm
from datetime import datetime

bp = Blueprint('admin', __name__, url_prefix='/admin')

@bp.route('/')
@admin_required
def index():
    user_count = User.query.count()
    request_count = Request.query.count()
    # Sum of all credit transactions that are positive (purchases)
    # This is a simplification.
    volume = db.session.query(db.func.sum(CreditTransaction.amount)).filter(CreditTransaction.amount > 0).scalar() or 0
    
    return render_template('admin/dashboard.html', 
                           user_count=user_count, 
                           request_count=request_count, 
                           volume=volume)

@bp.route('/users')
@admin_required
def users():
    users = User.query.all()
    form = AdminActionForm() # For the buttons
    return render_template('admin/users.html', users=users, form=form)

@bp.route('/categories', methods=['GET', 'POST'])
@admin_required
def categories():
    form = AddCategoryForm()
    # Populate parent choices
    parents = Category.query.filter(Category.parent_id == None).all()
    form.parent_id.choices = [(0, 'No Parent (Top Level)')] + [(c.id, c.name) for c in parents]
    
    if form.validate_on_submit():
        parent_id = form.parent_id.data if form.parent_id.data != 0 else None
        cat = Category(name=form.name.data, parent_id=parent_id)
        db.session.add(cat)
        db.session.commit()
        flash('Category added.')
        return redirect(url_for('admin.categories'))
            
    categories = Category.query.all()
    return render_template('admin/categories.html', categories=categories, form=form)

@bp.route('/users/<int:id>/toggle_block', methods=['POST'])
@admin_required
def toggle_block_user(id):
    form = AdminActionForm()
    if form.validate_on_submit():
        user = db.session.get(User, id)
        if user:
            user.is_blocked = not user.is_blocked
            db.session.commit()
            status = 'blocked' if user.is_blocked else 'unblocked'
            flash(f'User {user.username} has been {status}.')
    return redirect(url_for('admin.users'))

@bp.route('/users/<int:id>/verify', methods=['POST'])
@admin_required
def verify_user(id):
    form = AdminActionForm()
    if form.validate_on_submit():
        user = db.session.get(User, id)
        if user:
            user.is_verified = True
            db.session.commit()
            flash(f'User {user.username} verified.')
    return redirect(url_for('admin.users'))

@bp.route('/users/<int:id>/add_credits', methods=['POST'])
@admin_required
def add_credits(id):
    user = db.session.get(User, id)
    amount = request.form.get('amount', type=int)
    if user and amount:
        user.credits += amount
        trans = CreditTransaction(user_id=user.id, amount=amount, description="Admin Manual Adjustment")
        db.session.add(trans)
        db.session.commit()
        flash(f'Added {amount} credits to {user.username}.')
    return redirect(url_for('admin.users'))

@bp.route('/requests')
@admin_required
def requests():
    requests = Request.query.order_by(Request.timestamp.desc()).all()
    form = AdminActionForm()
    return render_template('admin/requests.html', requests=requests, form=form)

@bp.route('/requests/<int:id>/delete', methods=['POST'])
@admin_required
def delete_request(id):
    form = AdminActionForm()
    if form.validate_on_submit():
        req = db.session.get(Request, id)
        if req:
            db.session.delete(req)
            db.session.commit()
            flash('Request deleted.')
    return redirect(url_for('admin.requests'))

@bp.route('/tickers', methods=['GET', 'POST'])
@admin_required
def tickers():
    form = AddTickerForm()
    if form.validate_on_submit():
        ticker = Ticker(name=form.name.data, value=form.value.data, change_rate=form.change.data)
        db.session.add(ticker)
        db.session.commit()
        flash('Ticker added.')
        return redirect(url_for('admin.tickers'))
        
    tickers = Ticker.query.all()
    action_form = AdminActionForm()
    return render_template('admin/tickers.html', tickers=tickers, form=form, action_form=action_form)

@bp.route('/tickers/<int:id>/delete', methods=['POST'])
@admin_required
def delete_ticker(id):
    form = AdminActionForm()
    if form.validate_on_submit():
        ticker = db.session.get(Ticker, id)
        if ticker:
            db.session.delete(ticker)
            db.session.commit()
            flash('Ticker deleted.')
    return redirect(url_for('admin.tickers'))

@bp.route('/settings', methods=['GET', 'POST'])
@admin_required
def settings():
    setting = SiteSetting.query.first()
    if not setting:
        setting = SiteSetting()
        db.session.add(setting)
        db.session.commit()
    
    form = SiteSettingsForm(obj=setting)
    if form.validate_on_submit():
        setting.announcement = form.announcement.data
        setting.contact_info = form.contact_info.data
        db.session.commit()
        flash('Settings updated.')
        return redirect(url_for('admin.settings'))
        
    return render_template('admin/settings.html', form=form)

@bp.route('/transactions')
@admin_required
def transactions():
    transactions = CreditTransaction.query.order_by(CreditTransaction.timestamp.desc()).all()
    return render_template('admin/transactions.html', transactions=transactions)
