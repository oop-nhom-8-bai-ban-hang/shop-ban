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
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
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
    is_admin = db.Column(db.Boolean, nullable=False, default=False) # Cột mới

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
# (Hàm load_products_from_folders() giữ nguyên như cũ...)
def load_products_from_folders():
    categorized_products = {}
    # ... code y hệt như cũ ...
    return categorized_products
CATEGORIES = load_products_from_folders()

# --- CÁC TRANG CÔNG KHAI ---
@app.route('/')
def home():
    return render_template('index.html', categories=CATEGORIES)

@app.route('/product/<string:product_id>')
def product(product_id):
    # ... (code y hệt như cũ) ...
    abort(404)

# --- TRANG ĐĂNG NHẬP, ĐĂNG KÝ (Giữ nguyên) ---
@app.route("/register", methods=['GET', 'POST'])
def register():
    # ... (code y hệt như cũ) ...
    return render_template('register.html')

@app.route("/login", methods=['GET', 'POST'])
def login():
    # ... (code y hệt như cũ) ...
    return render_template('login.html')

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

# ==========================================================
# KHU VỰC DÀNH CHO ADMIN
# ==========================================================
@app.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    # Trang tổng quan cho admin
    return render_template('admin_dashboard.html')

@app.route('/admin/add_product', methods=['GET', 'POST'])
@login_required
@admin_required
def add_product():
    if request.method == 'POST':
        # Lấy thông tin từ form
        category = request.form.get('category')
        product_name_slug = request.form.get('product_name_slug') # Tên thư mục, ví dụ: 'nike-air-max-97'
        product_name_display = request.form.get('product_name_display') # Tên hiển thị, ví dụ: 'Nike Air Max 97'
        price = request.form.get('price')
        description = request.form.get('description')
        
        # Tạo thư mục sản phẩm
        product_path = os.path.join('static', category, product_name_slug)
        if os.path.exists(product_path):
            flash('Lỗi: Tên sản phẩm này đã tồn tại.', 'danger')
            return redirect(url_for('add_product'))
        os.makedirs(product_path)

        # Tạo file info.json
        info_data = {
            "price": price,
            "description": description,
            "variants": []
        }
        
        # Xử lý các file ảnh được upload
        uploaded_files = request.files.getlist('images')
        for file in uploaded_files:
            if file.filename != '':
                # Lưu file ảnh vào thư mục sản phẩm
                file.save(os.path.join(product_path, file.filename))
                # Thêm thông tin ảnh vào info.json
                # Tạm thời lấy tên file làm tên màu
                color_name = os.path.splitext(file.filename)[0].replace('-', ' ').title()
                info_data["variants"].append({"color": color_name, "image": file.filename})

        # Lưu file info.json
        with open(os.path.join(product_path, 'info.json'), 'w', encoding='utf-8') as f:
            json.dump(info_data, f, ensure_ascii=False, indent=2)

        flash(f'Đã thêm thành công sản phẩm: {product_name_display}!', 'success')
        return redirect(url_for('admin_dashboard'))

    return render_template('add_product.html')

# --- TỰ ĐỘNG TẠO DATABASE VÀ TÀI KHOẢN ADMIN ---
with app.app_context():
    db.create_all()
    admin_user = User.query.filter_by(username='admin').first()
    if not admin_user:
        hashed_password = bcrypt.generate_password_hash('admin123').decode('utf-8')
        # is_admin=True để cấp quyền admin
        new_admin = User(username='admin', password=hashed_password, is_admin=True)
        db.session.add(new_admin)
        db.session.commit()
        print("Đã tạo tài khoản admin mặc định với quyền quản trị.")
