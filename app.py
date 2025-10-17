from flask import Flask, render_template, abort
import os
import json

app = Flask(__name__)

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
