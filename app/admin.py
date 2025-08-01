from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import User, Client

admin = Blueprint('admin', __name__)

@admin.route('/')
@login_required
def index():
    if not current_user.is_admin:
        flash('ليس لديك صلاحية للوصول لهذه الصفحة', 'error')
        return redirect(url_for('main.index'))
    
    users = User.query.all()
    total_clients = Client.query.count()
    total_users = User.query.count()
    
    return render_template('admin.html', users=users, total_clients=total_clients, total_users=total_users)

@admin.route('/add_user', methods=['GET', 'POST'])
@login_required
def add_user():
    if not current_user.is_admin:
        flash('ليس لديك صلاحية للوصول لهذه الصفحة', 'error')
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        is_admin = 'is_admin' in request.form
        
        if User.query.filter_by(username=username).first():
            flash('اسم المستخدم موجود مسبقاً', 'error')
            return render_template('add_user.html')
        
        if User.query.filter_by(email=email).first():
            flash('البريد الإلكتروني موجود مسبقاً', 'error')
            return render_template('add_user.html')
        
        user = User(username=username, email=email, is_admin=is_admin)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash('تم إضافة المستخدم بنجاح', 'success')
        return redirect(url_for('admin.index'))
    
    return render_template('add_user.html')

@admin.route('/edit_user/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_user(id):
    if not current_user.is_admin:
        flash('ليس لديك صلاحية للوصول لهذه الصفحة', 'error')
        return redirect(url_for('main.index'))
    
    user = User.query.get_or_404(id)
    
    if request.method == 'POST':
        user.username = request.form['username']
        user.email = request.form['email']
        user.is_admin = 'is_admin' in request.form
        
        if request.form['password']:
            user.set_password(request.form['password'])
        
        db.session.commit()
        flash('تم تحديث بيانات المستخدم بنجاح', 'success')
        return redirect(url_for('admin.index'))
    
    return render_template('edit_user.html', user=user)

@admin.route('/delete_user/<int:id>')
@login_required
def delete_user(id):
    if not current_user.is_admin:
        flash('ليس لديك صلاحية للوصول لهذه الصفحة', 'error')
        return redirect(url_for('main.index'))
    
    user = User.query.get_or_404(id)
    
    if user.id == current_user.id:
        flash('لا يمكنك حذف حسابك الشخصي', 'error')
        return redirect(url_for('admin.index'))
    
    # Delete all clients associated with this user
    Client.query.filter_by(user_id=user.id).delete()
    
    db.session.delete(user)
    db.session.commit()
    flash('تم حذف المستخدم وجميع عملائه بنجاح', 'success')
    return redirect(url_for('admin.index')) 