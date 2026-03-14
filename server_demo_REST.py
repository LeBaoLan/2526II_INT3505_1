from flask import Flask, jsonify, request, make_response
import jwt
import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'

inventory = [
    {"id": 1, "name": "Sneaker", "price": 500},
    {"id": 2, "name": "Running Shoe", "price": 800}
]

# Danh sách user giả định thay cho VALID_KEYS
USERS = {"admin": "123456", "lebaolan": "password"}


@app.route('/login', methods=['POST'])
def login():
    auth = request.json
    if not auth or not auth.get('username') or not auth.get('password'):
        return jsonify({"error": "Thiếu thông tin đăng nhập"}), 400

    if USERS.get(auth['username']) == auth['password']:
        # Tạo JWT có thời hạn 30 phút
        token = jwt.encode({
            'user': auth['username'],
            'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=30)
        }, app.config['SECRET_KEY'], algorithm="HS256")

        return jsonify({"token": token})

    return jsonify({"error": "Sai tài khoản hoặc mật khẩu"}), 401


def check_jwt():
    # Lấy token từ header Authorization: Bearer <token>
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith("Bearer "):
        return False

    token = auth_header.split(" ")[1]
    try:
        # Giải mã và kiểm tra chữ ký
        jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
        return True
    except:
        return False


@app.route('/items', methods=['GET'])
def get_items():
    if not check_jwt():
        return jsonify({"error": "Token không hợp lệ hoặc đã hết hạn"}), 401

    res = make_response(jsonify(inventory))
    res.headers['Cache-Control'] = 'public, max-age=30'
    return res


@app.route('/items', methods=['POST'])
def add_item():
    if not check_jwt():
        return jsonify({"error": "Unauthorized"}), 401
    new_data = request.json
    inventory.append(new_data)
    return jsonify({"message": "Thêm thành công!", "item": new_data}), 201


@app.route('/items/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    if not check_jwt():
        return jsonify({"error": "Unauthorized"}), 401
    global inventory
    inventory = [item for item in inventory if item['id'] != item_id]
    return jsonify({"message": f"Đã xóa {item_id}"}), 200


if __name__ == '__main__':
    print("--- SERVER REST JWT (CACHEABLE) ĐANG CHẠY ---")
    app.run(port=5000)
