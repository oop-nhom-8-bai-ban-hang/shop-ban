from flask import Flask, render_template, abort
import os

app = Flask(__name__)

def load_products_by_folder_structure():
    """
    Quét các thư mục con trong 'static/shoes'. Mỗi thư mục con là một sản phẩm.
    Tự động tìm ảnh bìa, video, và các ảnh chi tiết.
    """
    products_dict = {}
    base_path = 'static/shoes'

    # Kiểm tra xem thư mục shoes có tồn tại không
    if not os.path.isdir(base_path):
        return {}

    # Lặp qua tất cả các mục trong 'static/shoes'
    for product_folder in os.listdir(base_path):
        folder_path = os.path.join(base_path, product_folder)

        # Chỉ xử lý nếu đó là một thư mục
        if os.path.isdir(folder_path):
            product_id = product_folder
            product_name = product_folder.replace('-', ' ').replace('_', ' ').title()
            
            # Tìm kiếm các file trong thư mục sản phẩm
            files_in_folder = os.listdir(folder_path)
            
            cover_image = None
            video_file = None
            detail_images = []

            # Phân loại file (ảnh bìa, video, ảnh chi tiết)
            image_extensions = ('.jpg', '.jpeg', '.png', '.webp')
            video_extensions = ('.mp4', '.mov', '.webm')

            # Ưu tiên tìm cover.jpg/.png làm ảnh bìa
            for f in files_in_folder:
                if f.startswith('cover.') and f.lower().endswith(image_extensions):
                    cover_image = os.path.join('shoes', product_folder, f)
                    break
            
            # Lặp lại để xử lý các file còn lại
            for f in files_in_folder:
                full_path = os.path.join('shoes', product_folder, f)
                
                # Nếu chưa có ảnh bìa, lấy ảnh đầu tiên tìm thấy
                if not cover_image and f.lower().endswith(image_extensions):
                    cover_image = full_path

                # Nếu là video
                if f.lower().endswith(video_extensions):
                    video_file = full_path
                # Nếu là ảnh và không phải ảnh bìa đã chọn
                elif f.lower().endswith(image_extensions) and full_path != cover_image:
                    detail_images.append(full_path)

            # Chỉ thêm sản phẩm nếu có ít nhất một ảnh bìa
            if cover_image:
                products_dict[product_id] = {
                    'name': product_name,
                    'cover_image': cover_image,
                    'video_file': video_file,
                    'detail_images': detail_images,
                    'price': 'Liên hệ', # Bạn có thể thêm file info.txt để đọc giá sau
                    'description': f'Mô tả chi tiết cho sản phẩm {product_name}.'
                }
                
    return products_dict

PRODUCTS = load_products_by_folder_structure()

@app.route('/')
def home():
    return render_template('index.html', products=PRODUCTS)

@app.route('/product/<string:product_id>')
def product(product_id):
    product_info = PRODUCTS.get(product_id)
    if not product_info:
        abort(404)
    return render_template('products.html', product=product_info)
