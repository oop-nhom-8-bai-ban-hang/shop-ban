from flask import Flask, render_template, abort

app = Flask(__name__)

# Dữ liệu này bây giờ CHỈ dùng cho trang chi tiết sản phẩm
CATEGORIES = {
    'Sản Phẩm Linh Tinh': [
        {
            'id': 'linh-tinh-ao-thun',
            'name': 'Áo Thun',
            'cover_image': 'linh-tinh/ao-thun/cover.jpg',
            'price': '150.000đ',
            'description': 'Mô tả chi tiết cho áo thun.'
            # Bạn có thể thêm các ảnh chi tiết và video vào đây nếu muốn
        },
        {
            'id': 'linh-tinh-quan-jean',
            'name': 'Quần Jean',
            'cover_image': 'linh-tinh/quan-jean/cover.png',
            'price': '250.000đ',
            'description': 'Mô tả chi tiết cho quần jean.'
        }
    ]
}

@app.route('/')
def home():
    # Trang chủ bây giờ không cần dữ liệu từ app.py nữa
    return render_template('index.html')

@app.route('/product/<string:product_id>')
def product(product_id):
    found_product = None
    # Vẫn tìm sản phẩm trong dữ liệu để hiển thị trang chi tiết
    for category_list in CATEGORIES.values():
        for p in category_list:
            if p['id'] == product_id:
                found_product = p
                break
        if found_product:
            break
    
    if not found_product:
        abort(404)
        
    # File products.html sẽ cần được tạo để hiển thị chi tiết sản phẩm
    return render_template('products.html', product=found_product)
