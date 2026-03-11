from flask import Flask, jsonify, request, make_response

app = Flask(__name__)

inventory = [
    {"id": 1, "name": "Sneaker", "price": 500},
    {"id": 2, "name": "Running Shoe", "price": 800}
]

VALID_KEYS = ["admin_key", "lebaolan"]


def check_auth():
    api_key = request.headers.get('X-API-KEY')
    return api_key in VALID_KEYS


@app.route('/items', methods=['GET'])
def get_items():
    if not check_auth():
        return jsonify({"error": "Unauthorized"}), 401

    # Tạo đối tượng response từ dữ liệu JSON
    res = make_response(jsonify(inventory))

    # THÊM NGUYÊN TẮC CACHEABLE:
    # max-age=30 nghĩa là dữ liệu này có hiệu lực trong 30 giây
    res.headers['Cache-Control'] = 'public, max-age=30'
    return res

# Các route POST và DELETE giữ nguyên như V3 (vì thường không cache các lệnh thay đổi dữ liệu)


@app.route('/items', methods=['POST'])
def add_item():
    if not check_auth():
        return jsonify({"error": "Unauthorized"}), 401
    new_data = request.json
    inventory.append(new_data)
    return jsonify({"message": "Thêm thành công!", "item": new_data}), 201


@app.route('/items/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    if not check_auth():
        return jsonify({"error": "Unauthorized"}), 401
    global inventory
    inventory = [item for item in inventory if item['id'] != item_id]
    return jsonify({"message": f"Đã xóa {item_id}"}), 200


if __name__ == '__main__':
    print("--- SERVER REST V4 (CACHEABLE) ĐANG CHẠY ---")
    app.run(port=5000)
