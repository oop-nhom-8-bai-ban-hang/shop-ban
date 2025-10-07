from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def home():
    # Lệnh này yêu cầu Flask tải file index.html từ thư mục 'templates'
    return render_template("index.html")

@app.route("/product/<name>")
def product(name):
    return f"<h1>Thông tin sản phẩm: {name}</h1><p>Đây chỉ là mô phỏng!</p>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
