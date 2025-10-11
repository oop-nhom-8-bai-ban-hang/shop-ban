from flask import Flask, render_template, abort

app = Flask(__name__)

# ==============================================================================
# THÊM SẢN PHẨM THỦ CÔNG TẠI ĐÂY
# ==============================================================================
# Chúng ta định nghĩa sẵn danh sách sản phẩm, không cần quét file nữa.
# Khi nào rảnh, bạn chỉ cần sửa lại "price" và "description" ở đây.
CATEGORIES = {
    'Sản Phẩm Linh Tinh': [
        {
            'id': 'linh-tinh-ao-thun',
            'name': 'Áo Thun',
            # QUAN TRỌNG: Đường dẫn ảnh này phải đúng với file trên GitHub của bạn
            'cover_image': 'linh-tinh/ao-thun/cover.jpg',
            'price': '150.000đ',
            'description': 'Mô tả chi tiết cho áo thun. Khi nào rảnh bạn sửa nhé.'
        },
        {
            'id': 'linh-tinh-quan-jean',
            'name': 'Quần Jean',
            # QUAN TRỌNG: Đường dẫn ảnh này phải đúng với file trên GitHub của bạn
            'cover_image': 'linh-tinh/quan-jean/cover.png',
            'price': '250.000đ',
            'description': 'Mô tả chi tiết cho quần jean. Khi nào rảnh bạn sửa nhé.'
        }
    ]
}

# ==============================================================================
# CÁC ROUTE KHÔNG THAY ĐỔI NHIỀU
# ==============================================================================
@app.route('/')
def home():
    # Trực tiếp gửi dữ liệu thủ công qua template
    return render_template('index.html', categories=CATEGORIES)

@app.route('/product/<string:product_id>')
def product(product_id):
    found_product = None
    # Tìm sản phẩm trong dữ liệu thủ công
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
