from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    # Gửi một biến đơn giản qua template để kiểm tra
    test_message = "DEBUG: App đang chạy thành công!"
    return render_template('index.html', message=test_message)

# Tạm thời vô hiệu hóa trang chi tiết sản phẩm
@app.route('/product/<string:product_id>')
def product(product_id):
    return f"Trang chi tiết cho sản phẩm: {product_id}"
