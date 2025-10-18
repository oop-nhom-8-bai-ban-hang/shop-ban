from flask import Flask, render_template, abort, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from flask_bcrypt import Bcrypt
from functools import wraps
import os
import json

app = Flask(__name__)

# --- CẤU HÌNH ---
app.config['SECRET_KEY'] = 'mot-chuoi-bi-mat-nao-do-rat-kho-doan'
# === DÒNG CODE ĐÃ SỬA LỖI ===
# Chỉ định lưu file database vào thư mục /tmp là thư mục duy nhất có thể ghi trên Vercel
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# --- KHỞI TẠO CÁC TIỆN ÍCH ---
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# --- NÂNG CẤP MODEL: THÊM CỘT is_admin ---
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- DECORATOR: HÀM KIỂM TRA QUYỀN ADMIN ---
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash("Bạn không có quyền truy cập trang này.", "danger")
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function

# --- LOGIC QUÉT SẢN PHẨM (Giữ nguyên) ---
CATEGORY_NAME_MAP = {
    'shoes': 'Giày Dép Thời Trang',
    'linh-tinh': 'Sản Phẩm Linh Tinh',
}
def load_products_from_folders():
    categorized_products = {}
    base_path = 'static'
    # ... (code quét file của bạn giữ nguyên ở đây) ...
    return categorized_products
CATEGORIES = load_products_from_folders()

# --- CÁC TRANG CÔNG KHAI ---
@app.route('/')
def home():
    return render_template('index.html', categories=CATEGORIES)

@app.route('/product/<string:product_id>')
def product(product_id):
    # ... (code của bạn giữ nguyên ở đây) ...
    abort(404)

# --- TRANG ĐĂNG NHẬP, ĐĂNG KÝ (Giữ nguyên) ---
@app.route("/register", methods=['GET', 'POST'])
def register():
    # ... (code của bạn giữ nguyên ở đây) ...
    return render_template('register.html')

@app.route("/login", methods=['GET', 'POST'])
def login():
    # ... (code của bạn giữ nguyên ở đây) ...
    return render_template('login.html')

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

# --- KHU VỰC DÀNH CHO ADMIN ---
@app.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    return render_template('admin_dashboard.html')

@app.route('/admin/add_product', methods=['GET', 'POST'])
@login_required
@admin_required
def add_product():
    # ... (code của bạn giữ nguyên ở đây) ...
    return render_template('add_product.html')

# --- TỰ ĐỘNG TẠO DATABASE VÀ TÀI KHOẢN ADMIN ---
with app.app_context():
    db.create_all()
    admin_user = User.query.filter_by(username='admin').first()
    if not admin_user:
        hashed_password = bcrypt.generate_password_hash('admin123').decode('utf-8')
        new_admin = User(username='admin', password=hashed_password, is_admin=True)
        db.session.add(new_admin)
        db.session.commit()
        print("Đã tạo tài khoản admin mặc định với quyền quản trị.")
