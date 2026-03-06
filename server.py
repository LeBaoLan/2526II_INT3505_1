from flask import Flask, jsonify, request

app = Flask(__name__)

# Giả lập Database
inventory = [
    {"id": 1, "name": "Sneaker", "price": 500},
    {"id": 2, "name": "Running Shoe", "price": 800}
]

# GET /items: Lấy danh sách sản phẩm


@app.route('/items', methods=['GET'])
def get_items():
    return jsonify(inventory)

# POST /items: Thêm một sản phẩm mới (Dữ liệu gửi trong Body)


@app.route('/items', methods=['POST'])
def add_item():
    new_data = request.json
    inventory.append(new_data)
    return jsonify({"message": "Thêm thành công!", "item": new_data}), 201

# DELETE /items/<id>: Xóa một sản phẩm cụ thể theo ID


@app.route('/items/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    global inventory
    # Kiểm tra xem ID có tồn tại không
    exists = any(item['id'] == item_id for item in inventory)
    if not exists:
        return jsonify({"message": "Không tìm thấy ID này!"}), 404

    inventory = [item for item in inventory if item['id'] != item_id]
    return jsonify({"message": f"Đã xóa sản phẩm ID {item_id}"}), 200


if __name__ == '__main__':
    print("--- SERVER REST V2 ĐANG CHẠY ---")
    app.run(port=5000)
