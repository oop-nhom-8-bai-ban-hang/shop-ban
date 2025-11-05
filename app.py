from flask import Flask, render_template, abort, redirect, url_for, request, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from flask_bcrypt import Bcrypt
from functools import wraps
import os
import json
from datetime import datetime
from werkzeug.utils import secure_filename
import secrets

app = Flask(__name__)

# --- CẤU HÌNH ---
app.config['SECRET_KEY'] = 'mot-chuoi-bi-mat-nao-do-rat-kho-doan'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/product_images'

# --- KHỞI TẠO CÁC TIỆN ÍCH ---
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# --- MODELS CHO DATABASE ---
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    products = db.relationship('Product', backref='seller', lazy=True)
    orders = db.relationship('Order', backref='customer', lazy=True)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    products = db.relationship('Product', backref='category', lazy=True)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_placed = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    items = db.Column(db.Text, nullable=False)
    total_price = db.Column(db.String(50), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

# --- CÁC TRANG CÔNG KHAI ---
@app.route('/')
def home():
    categories = Category.query.all()
    return render_template('index.html', categories=categories)

@app.route('/product/<int:product_id>')
def product(product_id):
    prod = Product.query.get_or_404(product_id)
    return render_template('products.html', product=prod)
# BẮT ĐẦU CODE HÀM TÌM KIẾM
@app.route('/search')
def search():
    query = request.args.get('query') # Lấy từ khóa 'query' từ URL
    if not query:
        return redirect(url_for('home')) # Nếu không gõ gì thì quay về trang chủ
    
    # Tìm tất cả sản phẩm có tên chứa từ khóa (không phân biệt hoa/thường)
    search_term = f"%{query}%"
    results = Product.query.filter(Product.name.ilike(search_term)).all()
    
    # Gửi kết quả sang một trang HTML mới
    return render_template('search_results.html', products=results, query=query)
# KẾT THÚC CODE HÀM TÌM KIẾM

# --- CHỨC NĂNG TÀI KHOẢN (Giữ nguyên) ---
@app.route("/register", methods=['GET', 'POST'])
def register():
    # ...
    return render_template('register.html')

@app.route("/login", methods=['GET', 'POST'])
def login():
    # ...
    return render_template('login.html')

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

# --- CHỨC NĂNG GIỎ HÀNG (Giữ nguyên) ---
@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    # ...
    return redirect(url_for('cart'))

@app.route('/cart')
@login_required
def cart():
    # ...
    return render_template('cart.html', cart_items=[], total_price=0)

@app.route('/checkout', methods=['POST'])
@login_required
def checkout():
    # ...
    return redirect(url_for('home'))

# ==========================================================
# KHU VỰC DÀNH CHO USER
# ==========================================================
def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], picture_fn)
    form_picture.save(picture_path)
    return picture_fn

@app.route('/my_products')
@login_required
def my_products():
    products = Product.query.filter_by(seller=current_user).order_by(Product.date_posted.desc()).all()
    return render_template('my_products.html', products=products)

@app.route('/add_product', methods=['GET', 'POST'])
@login_required
def add_product():
    categories = Category.query.all()
    if request.method == 'POST':
        name = request.form.get('name')
        price = request.form.get('price')
        description = request.form.get('description')
        category_id = request.form.get('category')
        image_file = 'default.jpg'
        if 'image' in request.files and request.files['image'].filename != '':
            image_file = save_picture(request.files['image'])
        
        new_prod = Product(name=name, price=price, description=description, category_id=category_id, image_file=image_file, seller=current_user)
        db.session.add(new_prod)
        db.session.commit()
        flash('Sản phẩm của bạn đã được đăng bán!', 'success')
        return redirect(url_for('my_products'))
    return render_template('add_product.html', categories=categories)

@app.route('/delete_product/<int:product_id>', methods=['POST'])
@login_required
def delete_product(product_id):
    prod = Product.query.get_or_404(product_id)
    if prod.seller != current_user and not current_user.is_admin:
        abort(403)
    # Xóa file ảnh cũ
    if prod.image_file != 'default.jpg':
        try:
            os.remove(os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], prod.image_file))
        except OSError:
            pass # Bỏ qua nếu file không tồn tại
    db.session.delete(prod)
    db.session.commit()
    flash('Đã xóa sản phẩm.', 'success')
    if current_user.is_admin:
        return redirect(url_for('admin_products'))
    return redirect(url_for('my_products'))

# ==========================================================
# KHU VỰC DÀNH CHO ADMIN
# ==========================================================
@app.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    return render_template('admin_dashboard.html')

@app.route('/admin/categories', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_categories():
    if request.method == 'POST':
        name = request.form.get('name')
        if name:
            new_cat = Category(name=name)
            db.session.add(new_cat)
            db.session.commit()
            flash('Đã tạo danh mục mới.', 'success')
            return redirect(url_for('admin_categories'))
    categories = Category.query.all()
    return render_template('admin_categories.html', categories=categories)

@app.route('/admin/delete_category/<int:category_id>', methods=['POST'])
@login_required
@admin_required
def delete_category(category_id):
    cat = Category.query.get_or_404(category_id)
    if cat.products:
        flash('Không thể xóa danh mục có chứa sản phẩm.', 'danger')
        return redirect(url_for('admin_categories'))
    db.session.delete(cat)
    db.session.commit()
    flash('Đã xóa danh mục.', 'success')
    return redirect(url_for('admin_categories'))

@app.route('/admin/products')
@login_required
@admin_required
def admin_products():
    all_products = Product.query.order_by(Product.date_posted.desc()).all()
    return render_template('admin_products.html', products=all_products)
    
# --- TỰ ĐỘNG TẠO DATABASE VÀ ADMIN ---
with app.app_context():
    db.create_all()
    if not User.query.filter_by(username='admin').first():
        hashed_password = bcrypt.generate_password_hash('admin123').decode('utf-8')
        new_admin = User(username='admin', password=hashed_password, is_admin=True)
        db.session.add(new_admin)
        db.session.commit()
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
