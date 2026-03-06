from flask import Flask, jsonify

app = Flask(__name__)

inventory = [
    {"id": 1, "name": "Giày Sneaker A", "price": 500},
    {"id": 2, "name": "Giày Chạy Bộ B", "price": 800}
]


@app.route('/items', methods=['GET'])
def get_items():
    return jsonify(inventory)


if __name__ == '__main__':
    print("Server đang chạy tại http://localhost:5000")
    app.run(port=5000)
