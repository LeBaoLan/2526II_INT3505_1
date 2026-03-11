from flask import Flask, jsonify

app = Flask(__name__)

books = [{"id": 1, "title": "Dế Mèn Phiêu Lưu Ký", "author": "Tô Hoài"}]

# NHẤT QUÁN: Luôn bọc kết quả vào một object có khóa "status" và "data"


def consistent_response(data, status_code=200):
    return jsonify({
        "status": "success" if status_code < 400 else "error",
        "data": data
    }), status_code


@app.route('/api/v1/books', methods=['GET'])
def get_books():
    return consistent_response(books)


@app.route('/api/v1/books/1', methods=['GET'])
def get_book():
    return consistent_response(books[0])


if __name__ == '__main__':
    app.run(port=5000)
