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
# === DÒNG CODE ĐÃ SỬA LỖI ===
# Chỉ định lưu file database vào thư mục /tmp là thư mục duy nhất có thể ghi trên Vercel
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/site.db'
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

# --- DECORATOR KIỂM TRA QUYỀN ADMIN ---
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash("Bạn không có quyền truy cập trang này.", "danger")
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function

# --- LOGIC QUÉT SẢN PHẨM ---
CATEGORY_NAME_MAP = {
    'shoes': 'Giày Dép Thời Trang',
    'linh-tinh': 'Sản Phẩm Linh Tinh',
}
def load_products_from_folders():
    categorized_products = {}
    base_path = 'static'
    sorted_folders = sorted(CATEGORY_NAME_MAP.keys(), key=lambda x: ('shoes' not in x, x))

    for folder_name in sorted_folders:
        display_name = CATEGORY_NAME_MAP[folder_name]
        folder_path = os.path.join(base_path, folder_name)
        product_list = []

        if os.path.isdir(folder_path):
            for product_folder in os.listdir(folder_path):
                product_path = os.path.join(folder_path, product_folder)

                if os.path.isdir(product_path):
                    product_id = f"{folder_name}-{product_folder}"
                    product_name = product_folder.replace('-', ' ').replace('_', ' ').title()
                    
                    info_path = os.path.join(product_path, 'info.json')
                    if os.path.exists(info_path):
                        try:
                            with open(info_path, 'r', encoding='utf-8') as f:
                                product_data = json.load(f)

                            if 'variants' in product_data and len(product_data['variants']) > 0:
                                cover_image_info = product_data['variants'][0]
                                cover_image_path = os.path.join(folder_name, product_folder, cover_image_info['image'])
                                
                                video_file = None
                                video_extensions = ('.mp4', '.mov', '.webm')
                                for file in os.listdir(product_path):
                                    if file.lower().endswith(video_extensions):
                                        video_file = os.path.join(folder_name, product_folder, file)
                                        break

                                product_list.append({
                                    'id': product_id,
                                    'name': product_name,
                                    'price': product_data.get('price', 'Liên hệ'),
                                    'description': product_data.get('description', '...'),
                                    'cover_image': cover_image_path,
                                    'variants': product_data['variants'],
                                    'video_file': video_file
                                })
                        except json.JSONDecodeError:
                            print(f"LỖI CÚ PHÁP: File {info_path} bị lỗi.")
                            continue
        if product_list:
            categorized_products[display_name] = product_list
    return categorized_products
CATEGORIES = load_products_from_folders()

# --- CÁC TRANG CÔNG KHAI ---
@app.route('/')
def home():
    return render_template('index.html', categories=CATEGORIES)

@app.route('/product/<string:product_id>')
def product(product_id):
    found_product = None
    for category_list in CATEGORIES.values():
        for p in category_list:
            if p['id'] == product_id:
                found_product = p
                break
        if found_product:
            break
    if not found_product:
        abort(404)
    return render_template('products.html', product=found_product)

# --- CHỨC NĂNG TÀI KHOẢN ---
@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated: return redirect(url_for('home'))
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Tên người dùng đã tồn tại. Vui lòng chọn tên khác.', 'danger')
            return redirect(url_for('register'))
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(username=username, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Tài khoản đã được tạo thành công! Bây giờ bạn có thể đăng nhập.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated: return redirect(url_for('home'))
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user, remember=True)
            return redirect(url_for('home'))
        else:
            flash('Đăng nhập thất bại. Vui lòng kiểm tra lại tên đăng nhập và mật khẩu.', 'danger')
    return render_template('login.html')

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

# --- CHỨC NĂNG GIỎ HÀNG VÀ ĐẶT HÀNG ---
@app.route('/add_to_cart/<string:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    found_product = None
    for category_list in CATEGORIES.values():
        for p in category_list:
            if p['id'] == product_id: found_product = p; break
    if not found_product:
        flash('Không tìm thấy sản phẩm!', 'danger')
        return redirect(url_for('home'))
    if 'cart' not in session: session['cart'] = []
    for item in session['cart']:
        if item['id'] == product_id:
            flash(f"{found_product['name']} đã có trong giỏ hàng.", 'info')
            return redirect(url_for('cart'))
    cart_item = {'id': found_product['id'], 'name': found_product['name'], 'price': found_product['price'], 'cover_image': found_product['cover_image'], 'quantity': 1}
    session['cart'].append(cart_item)
    session.modified = True
    flash(f"Đã thêm {found_product['name']} vào giỏ hàng!", 'success')
    return redirect(url_for('cart'))

@app.route('/cart')
@login_required
def cart():
    cart_items = session.get('cart', [])
    total_price = sum(int(item['price'].replace('.', '').replace('đ', '')) * item['quantity'] for item in cart_items)
    return render_template('cart.html', cart_items=cart_items, total_price=total_price)

@app.route('/checkout', methods=['POST'])
@login_required
def checkout():
    cart_items = session.get('cart', [])
    if not cart_items: return redirect(url_for('home'))
    total_price = sum(int(item['price'].replace('.', '').replace('đ', '')) * item['quantity'] for item in cart_items)
    new_order = Order(customer=current_user, items=json.dumps(cart_items), total_price=f"{total_price:,}đ")
    db.session.add(new_order)
    db.session.commit()
    session.pop('cart', None)
    flash('Bạn đã đặt hàng thành công! Cảm ơn bạn đã mua sắm.', 'success')
    return redirect(url_for('home'))

# --- KHU VỰC ADMIN ---
@app.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    return render_template('admin_dashboard.html')

@app.route('/admin/add_product', methods=['GET', 'POST'])
@login_required
@admin_required
def add_product():
    if request.method == 'POST':
        category = request.form.get('category')
        product_name_slug = request.form.get('product_name_slug')
        product_name_display = request.form.get('product_name_display')
        price = request.form.get('price')
        description = request.form.get('description')
        product_path = os.path.join('static', category, product_name_slug)
        if os.path.exists(product_path):
            flash('Lỗi: Tên sản phẩm này đã tồn tại.', 'danger')
            return redirect(url_for('add_product'))
        os.makedirs(product_path)
        info_data = {"price": price, "description": description, "variants": []}
        uploaded_files = request.files.getlist('images')
        for file in uploaded_files:
            if file.filename != '':
                file.save(os.path.join(product_path, file.filename))
                color_name = os.path.splitext(file.filename)[0].replace('-', ' ').title()
                info_data["variants"].append({"color": color_name, "image": file.filename})
        with open(os.path.join(product_path, 'info.json'), 'w', encoding='utf-8') as f:
            json.dump(info_data, f, ensure_ascii=False, indent=2)
        flash(f'Đã thêm thành công sản phẩm: {product_name_display}!', 'success')
        return redirect(url_for('admin_dashboard'))
    return render_template('add_product.html')

@app.route('/admin/orders')
@login_required
@admin_required
def admin_orders():
    all_orders = Order.query.order_by(Order.date_placed.desc()).all()
    return render_template('admin_orders.html', orders=all_orders)

# --- TỰ ĐỘNG TẠO DATABASE VÀ ADMIN ---
with app.app_context():
    db.create_all()
    admin_user = User.query.filter_by(username='admin').first()
    if not admin_user:
        hashed_password = bcrypt.generate_password_hash('admin123').decode('utf-8')
        new_admin = User(username='admin', password=hashed_password, is_admin=True)
        db.session.add(new_admin)
        db.session.commit()
        print("Đã tạo tài khoản admin mặc định với quyền quản trị.")
