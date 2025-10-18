from flask import Flask, render_template, abort, redirect, url_for, request, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from flask_bcrypt import Bcrypt
from functools import wraps
import os
import json
from datetime import datetime

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

# --- CÁC MODEL CHO DATABASE ---
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    orders = db.relationship('Order', backref='customer', lazy=True)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_placed = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    items = db.Column(db.Text, nullable=False) # Lưu sản phẩm dưới dạng JSON text
    total_price = db.Column(db.String(50), nullable=False)

# --- DECORATOR KIỂM TRA QUYỀN ADMIN (Giữ nguyên) ---
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
    # ... (code hàm này giữ nguyên)
    return {}
CATEGORIES = load_products_from_folders()

# --- CÁC TRANG CÔNG KHAI ---
@app.route('/')
def home():
    return render_template('index.html', categories=CATEGORIES)

@app.route('/product/<string:product_id>')
def product(product_id):
    # ... (code hàm này giữ nguyên)
    abort(404)

# --- CHỨC NĂNG TÀI KHOẢN (Giữ nguyên) ---
@app.route("/register", methods=['GET', 'POST'])
def register():
    # ... (code giữ nguyên)
    return render_template('register.html')

@app.route("/login", methods=['GET', 'POST'])
def login():
    # ... (code giữ nguyên)
    return render_template('login.html')

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

# ==========================================================
# CHỨC NĂNG GIỎ HÀNG VÀ ĐẶT HÀNG MỚI
# ==========================================================
@app.route('/add_to_cart/<string:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    # Lấy thông tin sản phẩm từ hệ thống file (bạn có thể chuyển sang database sau này)
    found_product = None
    for category_list in CATEGORIES.values():
        for p in category_list:
            if p['id'] == product_id:
                found_product = p
                break
    
    if not found_product:
        flash('Không tìm thấy sản phẩm!', 'danger')
        return redirect(url_for('home'))

    # Khởi tạo giỏ hàng trong session nếu chưa có
    if 'cart' not in session:
        session['cart'] = []

    # Kiểm tra xem sản phẩm đã có trong giỏ chưa
    for item in session['cart']:
        if item['id'] == product_id:
            flash(f"{found_product['name']} đã có trong giỏ hàng.", 'info')
            return redirect(url_for('cart'))

    # Thêm sản phẩm vào giỏ
    cart_item = {
        'id': found_product['id'],
        'name': found_product['name'],
        'price': found_product['price'],
        'cover_image': found_product['cover_image'],
        'quantity': 1 # Mặc định số lượng là 1
    }
    session['cart'].append(cart_item)
    session.modified = True # Báo cho session biết là nó đã bị thay đổi
    flash(f"Đã thêm {found_product['name']} vào giỏ hàng!", 'success')
    return redirect(url_for('cart'))

@app.route('/cart')
@login_required
def cart():
    cart_items = session.get('cart', [])
    total_price = 0
    for item in cart_items:
        # Chuyển đổi giá từ chuỗi (ví dụ: "3.500.000đ") sang số
        price_as_number = int(item['price'].replace('.', '').replace('đ', ''))
        total_price += price_as_number * item['quantity']

    return render_template('cart.html', cart_items=cart_items, total_price=total_price)

@app.route('/checkout', methods=['POST'])
@login_required
def checkout():
    cart_items = session.get('cart', [])
    if not cart_items:
        return redirect(url_for('home'))

    total_price = 0
    for item in cart_items:
        price_as_number = int(item['price'].replace('.', '').replace('đ', ''))
        total_price += price_as_number * item['quantity']
    
    # Tạo đơn hàng mới và lưu vào database
    new_order = Order(
        customer=current_user,
        items=json.dumps(cart_items), # Chuyển danh sách sản phẩm thành chuỗi JSON
        total_price=f"{total_price:,}đ" # Định dạng lại giá tiền
    )
    db.session.add(new_order)
    db.session.commit()

    # Xóa giỏ hàng
    session.pop('cart', None)

    flash('Bạn đã đặt hàng thành công! Cảm ơn bạn đã mua sắm.', 'success')
    return redirect(url_for('home'))


# ==========================================================
# KHU VỰC ADMIN (Nâng cấp)
# ==========================================================
@app.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    return render_template('admin_dashboard.html')

@app.route('/admin/add_product', methods=['GET', 'POST'])
@login_required
@admin_required
def add_product():
    # ... (code giữ nguyên)
    return render_template('add_product.html')

@app.route('/admin/orders')
@login_required
@admin_required
def admin_orders():
    # Lấy tất cả đơn hàng từ database
    all_orders = Order.query.order_by(Order.date_placed.desc()).all()
    return render_template('admin_orders.html', orders=all_orders)

# --- TỰ ĐỘNG TẠO DATABASE VÀ ADMIN ---
with app.app_context():
    db.create_all()
    # ... (code tạo admin giữ nguyên)
