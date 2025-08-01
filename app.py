from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here-change-this-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///clients.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    call_date = db.Column(db.DateTime, default=datetime.utcnow)
    response = db.Column(db.String(50), nullable=False)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('clients', lazy=True))

    def __repr__(self):
        return f'<Client {self.name}>'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
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

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            flash('تم تسجيل الدخول بنجاح', 'success')
            return redirect(url_for('index'))
        else:
            flash('اسم المستخدم أو كلمة المرور غير صحيحة', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        if User.query.filter_by(username=username).first():
            flash('اسم المستخدم موجود مسبقاً', 'error')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            flash('البريد الإلكتروني موجود مسبقاً', 'error')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('كلمات المرور غير متطابقة', 'error')
            return render_template('register.html')
        
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash('تم إنشاء الحساب بنجاح، يمكنك الآن تسجيل الدخول', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('تم تسجيل الخروج بنجاح', 'success')
    return redirect(url_for('login'))

@app.route('/add_client', methods=['GET', 'POST'])
@login_required
def add_client():
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        response = request.form['response']
        notes = request.form['notes']
        
        if not name or not phone or not response:
            flash('يرجى ملء جميع الحقول المطلوبة', 'error')
            return redirect(url_for('add_client'))
        
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
        return redirect(url_for('index'))
    
    return render_template('add_client.html')

@app.route('/edit_client/<int:id>', methods=['GET', 'POST'])
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
        return redirect(url_for('index'))
    
    return render_template('edit_client.html', client=client)

@app.route('/delete_client/<int:id>')
@login_required
def delete_client(id):
    client = Client.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    db.session.delete(client)
    db.session.commit()
    flash('تم حذف العميل بنجاح', 'success')
    return redirect(url_for('index'))

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html')

@app.route('/admin')
@login_required
def admin():
    if not current_user.is_admin:
        flash('ليس لديك صلاحية للوصول لهذه الصفحة', 'error')
        return redirect(url_for('index'))
    
    users = User.query.all()
    total_clients = Client.query.count()
    total_users = User.query.count()
    
    return render_template('admin.html', users=users, total_clients=total_clients, total_users=total_users)

@app.route('/admin/add_user', methods=['GET', 'POST'])
@login_required
def add_user():
    if not current_user.is_admin:
        flash('ليس لديك صلاحية للوصول لهذه الصفحة', 'error')
        return redirect(url_for('index'))
    
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
        return redirect(url_for('admin'))
    
    return render_template('add_user.html')

@app.route('/admin/edit_user/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_user(id):
    if not current_user.is_admin:
        flash('ليس لديك صلاحية للوصول لهذه الصفحة', 'error')
        return redirect(url_for('index'))
    
    user = User.query.get_or_404(id)
    
    if request.method == 'POST':
        user.username = request.form['username']
        user.email = request.form['email']
        user.is_admin = 'is_admin' in request.form
        
        if request.form['password']:
            user.set_password(request.form['password'])
        
        db.session.commit()
        flash('تم تحديث بيانات المستخدم بنجاح', 'success')
        return redirect(url_for('admin'))
    
    return render_template('edit_user.html', user=user)

@app.route('/admin/delete_user/<int:id>')
@login_required
def delete_user(id):
    if not current_user.is_admin:
        flash('ليس لديك صلاحية للوصول لهذه الصفحة', 'error')
        return redirect(url_for('index'))
    
    user = User.query.get_or_404(id)
    
    if user.id == current_user.id:
        flash('لا يمكنك حذف حسابك الشخصي', 'error')
        return redirect(url_for('admin'))
    
    # Delete all clients associated with this user
    Client.query.filter_by(user_id=user.id).delete()
    
    db.session.delete(user)
    db.session.commit()
    flash('تم حذف المستخدم وجميع عملائه بنجاح', 'success')
    return redirect(url_for('admin'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Create admin user if not exists
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin = User(username='admin', email='admin@example.com', is_admin=True)
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("Admin user created: username='admin', password='admin123'")
    app.run(debug=True) 