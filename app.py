from flask import Flask, render_template, abort
import os
import json

app = Flask(__name__)

# TẠM THỜI CHỈ QUÉT "linh-tinh"
CATEGORY_NAME_MAP = {
    'linh-tinh': 'Sản Phẩm Linh Tinh',
}

def load_products_from_folders():
    categorized_products = {}
    base_path = 'static'

    for folder_name, display_name in CATEGORY_NAME_MAP.items():
        folder_path = os.path.join(base_path, folder_name)
        product_list = []

        if os.path.isdir(folder_path):
            for product_folder in os.listdir(folder_path):
                product_path = os.path.join(folder_path, product_folder)

                if os.path.isdir(product_path):
                    product_id = f"{folder_name}-{product_folder}"
                    product_name = product_folder.replace('-', ' ').replace('_', ' ').title()
                    
                    product_info = { 'price': 'Liên hệ', 'description': '...' }
                    info_path = os.path.join(product_path, 'info.json')
                    if os.path.exists(info_path):
                        with open(info_path, 'r', encoding='utf-8') as f:
                            product_info.update(json.load(f))

                    # Tìm file có tên bắt đầu bằng "cover."
                    cover_image_path = None
                    for file in os.listdir(product_path):
                        if file.lower().startswith('cover.') and file.lower().endswith(('.jpg', '.png', '.jpeg', '.webp')):
                            cover_image_path = os.path.join(folder_name, product_folder, file)
                            break
                    
                    if cover_image_path:
                        product_list.append({
                            'id': product_id,
                            'name': product_name,
                            'cover_image': cover_image_path,
                            **product_info
                        })

        if product_list:
            categorized_products[display_name] = product_list

    return categorized_products

CATEGORIES = load_products_from_folders()

# Các route không thay đổi
@app.route('/')
def home():
    sorted_categories = dict(sorted(CATEGORIES.items()))
    return render_template('index.html', categories=sorted_categories)

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
