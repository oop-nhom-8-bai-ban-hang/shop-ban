from flask import Flask, render_template, request, redirect, url_for
import os

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/confirm', methods=['POST'])
def confirm():
    # Khi người dùng nhấn nút "Xác nhận"
    return redirect(url_for('shop'))

@app.route('/shop')
def shop():
    return render_template('shop.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
