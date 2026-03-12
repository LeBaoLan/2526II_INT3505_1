from flask import Flask, jsonify, request

app = Flask(__name__)

# Giả lập Database
books = [
    {"id": 1, "title": "Dế Mèn Phiêu Lưu Ký", "author": "Tô Hoài"}
]


def send_response(data=None, message=None, status_code=200):
    # Tính nhất quán (V1): Luôn có 'status' và 'data'
    # Tính dễ hiểu (V2): Có thêm 'message' và dùng đúng 'status_code'

    success = status_code < 400
    response = {
        "status": "success" if success else "error",
        "data": data,
        "message": message
    }

    # Loại bỏ các trường None để JSON sạch sẽ hơn
    response = {k: v for k, v in response.items() if v is not None}

    return jsonify(response), status_code


@app.route('/api/books', methods=['GET'])
def get_books():
    # Nhất quán: Trả về danh sách trong 'data'
    return send_response(data=books)


@app.route('/api/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    book = next((b for b in books if b['id'] == book_id), None)
    if book:
        return send_response(data=book)

    # Dễ hiểu: Báo lỗi 404 kèm thông điệp cụ thể
    return send_response(message=f"Không tìm thấy sách ID {book_id}", status_code=404)


@app.route('/api/books', methods=['POST'])
def add_book():
    data = request.json
    if not data or 'title' not in data:
        # Dễ hiểu: Báo lỗi 400 khi dữ liệu sai
        return send_response(message="Dữ liệu không hợp lệ: Thiếu 'title'", status_code=400)

    books.append(data)
    return send_response(data=data, message="Đã thêm sách mới", status_code=201)


if __name__ == '__main__':
    print("--- SERVER CONSISTENCY & CLARITY ---")
    app.run(port=5000)
