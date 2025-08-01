from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import Client
from datetime import datetime

main = Blueprint('main', __name__)

@main.route('/')
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    # Get filter parameters
    response_filter = request.args.get('response_filter', '')
    date_filter = request.args.get('date_filter', '')
    search_query = request.args.get('query', '')
    
    # Build query
    query = Client.query.filter_by(user_id=current_user.id)
    
    if response_filter:
        query = query.filter(Client.response == response_filter)
    
    if date_filter:
        if date_filter == 'today':
            query = query.filter(db.func.date(Client.call_date) == db.func.date(db.func.now()))
        elif date_filter == 'week':
            query = query.filter(Client.call_date >= db.func.date(db.func.now(), '-7 days'))
        elif date_filter == 'month':
            query = query.filter(Client.call_date >= db.func.date(db.func.now(), '-30 days'))
    
    if search_query:
        query = query.filter(
            db.or_(
                Client.name.contains(search_query),
                Client.phone.contains(search_query),
                Client.response.contains(search_query),
                Client.notes.contains(search_query)
            )
        )
    
    # Get paginated results
    clients = query.order_by(Client.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    # Get unique responses for filter dropdown
    responses = db.session.query(Client.response).distinct().all()
    responses = [r[0] for r in responses if r[0]]
    
    return render_template('index.html', 
                         clients=clients, 
                         responses=responses,
                         response_filter=response_filter,
                         date_filter=date_filter,
                         search_query=search_query)

@main.route('/add_client', methods=['GET', 'POST'])
@login_required
def add_client():
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        response = request.form['response']
        notes = request.form['notes']
        
        if not name or not phone or not response:
            flash('يرجى ملء جميع الحقول المطلوبة', 'error')
            return redirect(url_for('main.add_client'))
        
        new_client = Client(
            name=name, 
            phone=phone, 
            response=response, 
            notes=notes,
            user_id=current_user.id
        )
        db.session.add(new_client)
        db.session.commit()
        
        flash('تم إضافة العميل بنجاح', 'success')
        return redirect(url_for('main.index'))
    
    return render_template('add_client.html')

@main.route('/edit_client/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_client(id):
    client = Client.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    
    if request.method == 'POST':
        client.name = request.form['name']
        client.phone = request.form['phone']
        client.response = request.form['response']
        client.notes = request.form['notes']
        client.call_date = datetime.utcnow()
        
        db.session.commit()
        flash('تم تحديث بيانات العميل بنجاح', 'success')
        return redirect(url_for('main.index'))
    
    return render_template('edit_client.html', client=client)

@main.route('/delete_client/<int:id>')
@login_required
def delete_client(id):
    client = Client.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    db.session.delete(client)
    db.session.commit()
    flash('تم حذف العميل بنجاح', 'success')
    return redirect(url_for('main.index'))

@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html') 