from flask import Flask, jsonify, request

app = Flask(__name__)

# Giả lập Database
inventory = [
    {"id": 1, "name": "Sneaker", "price": 500},
    {"id": 2, "name": "Running Shoe", "price": 800}
]

# Danh sách API Key hợp lệ cho nguyên tắc Stateless
VALID_KEYS = ["admin_key", "lebaolan"]


def check_auth():
    # Server không nhớ ai cả, mỗi lần gọi phải gửi Key qua Header
    api_key = request.headers.get('X-API-KEY')
    return api_key in VALID_KEYS


@app.route('/items', methods=['GET'])
def get_items():
    if not check_auth():
        # SỬA LỖI: Trả về dictionary chuẩn để jsonify không bị lỗi
        return jsonify({"error": "Từ chối truy cập! Thiếu định danh."}), 401
    return jsonify(inventory)


@app.route('/items', methods=['POST'])
def add_item():
    if not check_auth():
        return jsonify({"error": "Từ chối truy cập! Thiếu định danh."}), 401
    new_data = request.json
    inventory.append(new_data)
    return jsonify({"message": "Thêm thành công!", "item": new_data}), 201


@app.route('/items/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    if not check_auth():
        return jsonify({"error": "Từ chối truy cập! Thiếu định danh."}), 401
    global inventory
    exists = any(item['id'] == item_id for item in inventory)
    if not exists:
        return jsonify({"message": "Không tìm thấy ID này!"}), 404

    inventory = [item for item in inventory if item['id'] != item_id]
    return jsonify({"message": f"Đã xóa sản phẩm ID {item_id}"}), 200


if __name__ == '__main__':
    print("--- SERVER REST V3 (STATELESS) ĐANG CHẠY ---")
    app.run(port=5000)
