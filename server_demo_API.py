from flask import Flask, jsonify, request

app = Flask(__name__)

books = [
    {"id": 1, "title": "Dế Mèn Phiêu Lưu Ký", "author": "Tô Hoài"}
]

# Hàm bổ trợ để đảm bảo tính nhất quán (từ V1) nhưng thêm tính dễ hiểu (V2)


def response_builder(data=None, message=None, status_code=200):
    status = "success" if status_code < 400 else "error"
    payload = {"status": status}

    if data is not None:
        payload["data"] = data
    if message is not None:
        payload["message"] = message  # Thông báo rõ ràng

    return jsonify(payload), status_code


@app.route('/api/v2/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    book = next((b for b in books if b['id'] == book_id), None)

    if book:
        return response_builder(data=book)

    # DỄ HIỂU: Trả về 404 thay vì 200 kèm nội dung trống
    return response_builder(message=f"Không tìm thấy sách với ID {book_id}", status_code=404)


@app.route('/api/v2/books', methods=['POST'])
def add_book():
    data = request.json

    # DỄ HIỂU: Kiểm tra dữ liệu và trả về lỗi 400 (Bad Request) nếu thiếu thông tin
    if not data or 'title' not in data:
        return response_builder(message="Thiếu trường 'title' bắt buộc", status_code=400)

    books.append(data)
    return response_builder(data=data, message="Thêm sách mới thành công", status_code=201)


if __name__ == '__main__':
    print("--- API V2 (CLARITY) ĐANG CHẠY ---")
    app.run(port=5000)
