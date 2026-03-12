from flask import Flask, jsonify, request

app = Flask(__name__)

# Giả lập Database với 10 cuốn sách (Để test Dễ mở rộng - Phân trang)
books = [
    {"id": i, "title": f"Lập trình REST tập {i}", "author": "Hưng"}
    for i in range(1, 11)
]


def send_rest_response(data=None, message=None, metadata=None, status_code=200):
    # V1: Tính nhất quán (Luôn có status và data)
    # V2: Tính dễ hiểu (Có message và status_code chuẩn)
    # V3: Tính dễ mở rộng (Có metadata để phân trang/thêm tính năng)

    success = status_code < 400
    response = {
        "status": "success" if success else "error",
        "message": message,
        "metadata": metadata,
        "data": data
    }
    # Loại bỏ các trường trống để JSON gọn hơn
    response = {k: v for k, v in response.items() if v is not None}
    return jsonify(response), status_code


@app.route('/api/v3/books', methods=['GET'])
def get_books():
    # V3: Dễ mở rộng qua Query Parameters (Phân trang)
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 3))

        start = (page - 1) * limit
        end = start + limit
        paginated_items = books[start:end]

        if not paginated_items and page > 1:
            # V2: Dễ hiểu - Báo lỗi khi vượt quá số trang hiện có
            return send_rest_response(message="Trang này không có dữ liệu", status_code=404)

        meta = {
            "total": len(books),
            "page": page,
            "limit": limit
        }
        return send_rest_response(data=paginated_items, metadata=meta)
    except ValueError:
        # V2: Dễ hiểu - Báo lỗi khi người dùng nhập chữ thay vì số
        return send_rest_response(message="Tham số page/limit phải là số nguyên", status_code=400)


@app.route('/api/v3/books', methods=['POST'])
def add_book():
    data = request.json
    # V2: Dễ hiểu - Kiểm tra ràng buộc dữ liệu
    if not data or 'title' not in data:
        return send_rest_response(message="Lỗi: Thiếu tiêu đề sách (title)", status_code=400)

    books.append(data)
    return send_rest_response(data=data, message="Thêm thành công", status_code=201)


if __name__ == '__main__':
    print("--- SERVER FINAL: CONSISTENCY + CLARITY + EXTENSIBILITY ---")
    app.run(port=5000)
