from flask import Flask, render_template, abort
import os
import json

app = Flask(__name__)

def load_categorized_products():
    """
    Quét thư mục static, tự động phân loại sản phẩm vào các khu vực
    dựa trên thư mục con.
    """
    # Cấu trúc dữ liệu mới: {'Tên Khu Vực': [danh sách sản phẩm]}
    categorized_products = {}
    base_path = 'static'
    files_to_ignore = ['logo', 'do_ngu', 'background_music']
    image_extensions = ('.png', '.jpg', '.jpeg', '.webp')

    # --- XỬ LÝ CÁC KHU VỰC TỪ THƯ MỤC CON ---
    for category_folder in os.listdir(base_path):
        category_path = os.path.join(base_path, category_folder)
        
        # Chỉ xử lý nếu là thư mục và không phải thư mục hệ thống
        if os.path.isdir(category_path) and not category_folder.startswith('__'):
            category_name = category_folder.replace('-', ' ').replace('_', ' ').title()
            product_list = []

            # (Logic quét sản phẩm bên trong thư mục category, tương tự như trước)
            # Bạn có thể kết hợp cả 2 kiểu: sản phẩm là thư mục con hoặc file lẻ
            # Ví dụ đơn giản: quét các file lẻ trong thư mục category
            for filename in os.listdir(category_path):
                if filename.lower().endswith(image_extensions):
                    product_id = f"{category_folder}-{os.path.splitext(filename)[0]}" # Tạo ID duy nhất
                    product_name = os.path.splitext(filename)[0].replace('_', ' ').title()

                    product_info = {'price': 'Liên hệ', 'description': '...'}
                    json_path = os.path.join(category_path, f"{os.path.splitext(filename)[0]}.json")
                    if os.path.exists(json_path):
                        with open(json_path, 'r', encoding='utf-8') as f:
                            product_info.update(json.load(f))
                    
                    product_list.append({
                        'id': product_id,
                        'name': product_name,
                        'cover_image': os.path.join(category_folder, filename),
                        **product_info
                    })
            
            if product_list:
                categorized_products[category_name] = product_list

    # --- XỬ LÝ CÁC SẢN PHẨM LẺ TRONG STATIC -> GOM VÀO "LINH TINH" ---
    miscellaneous_products = []
    for filename in os.listdir(base_path):
        # Chỉ xử lý nếu là file (không phải thư mục)
        if os.path.isfile(os.path.join(base_path, filename)) and filename.lower().endswith(image_extensions):
            product_id = os.path.splitext(filename)[0]
            
            if product_id.lower() in [name.lower() for name in files_to_ignore]:
                continue
            
            product_name = product_id.replace('_', ' ').title()
            
            product_info = {'price': 'Liên hệ', 'description': '...'}
            json_path = os.path.join(base_path, f"{product_id}.json")
            if os.path.exists(json_path):
                with open(json_path, 'r', encoding='utf-8') as f:
                    product_info.update(json.load(f))
            
            miscellaneous_products.append({
                'id': product_id,
                'name': product_name,
                'cover_image': filename,
                **product_info
            })

    if miscellaneous_products:
        categorized_products['Linh Tinh'] = miscellaneous_products

    return categorized_products

# Dùng một tên biến mới để rõ ràng hơn
CATEGORIES = load_categorized_products()

@app.route('/')
def home():
    return render_template('index.html', categories=CATEGORIES)

# Route chi tiết sản phẩm cần điều chỉnh nhỏ để tìm kiếm sản phẩm trong các category
@app.route('/product/<string:product_id>')
def product(product_id):
    found_product = None
    for category in CATEGORIES.values():
        for p in category:
            if p['id'] == product_id:
                found_product = p
                break
        if found_product:
            break
    
    if not found_product:
        abort(404)
        
    # Trang products.html không cần thay đổi nhiều
    return render_template('products.html', product=found_product)
