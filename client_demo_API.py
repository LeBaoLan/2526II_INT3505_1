import requests


def run_demo_v2():
    print("=== KIỂM CHỨNG TÍNH DỄ HIỂU (CLARITY) ===\n")

    # 1. Thử lấy một cuốn sách không tồn tại (ID 99)
    print("--- Case 1: Tìm sách không tồn tại ---")
    res1 = requests.get("http://localhost:5000/api/v2/books/99")
    print(f"Status: {res1.status_code}")
    print(f"Phản hồi: {res1.json()}")

    # 2. Thử thêm sách nhưng thiếu tiêu đề (title)
    print("\n--- Case 2: Thêm sách thiếu dữ liệu ---")
    res2 = requests.post(
        "http://localhost:5000/api/v2/books", json={"author": "Hưng"})
    print(f"Status: {res2.status_code}")
    print(f"Phản hồi: {res2.json()}")

    # 3. Thêm sách đúng chuẩn
    print("\n--- Case 3: Thêm sách thành công ---")
    res3 = requests.post("http://localhost:5000/api/v2/books",
                         json={"id": 2, "title": "Lập trình REST"})
    print(f"Status: {res3.status_code}")
    print(f"Phản hồi: {res3.json()}")


if __name__ == "__main__":
    run_demo_v2()
