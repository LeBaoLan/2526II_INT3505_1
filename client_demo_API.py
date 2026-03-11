import requests


def run_demo_v1():
    endpoints = [
        "http://localhost:5000/api/v1/books",
        "http://localhost:5000/api/v1/books/1"
    ]

    print("=== KIỂM CHỨNG TÍNH NHẤT QUÁN (CONSISTENCY) ===")

    for url in endpoints:
        print(f"\nĐang gọi: {url}")
        response = requests.get(url)
        json_data = response.json()

        # Kiểm chứng: Luôn có khóa 'status' và 'data'
        print(f"Mã trạng thái: {response.status_code}")
        print(f"Cấu trúc JSON nhận được: {list(json_data.keys())}")
        print(f"Nội dung 'data': {json_data['data']}")


if __name__ == "__main__":
    try:
        run_demo_v1()
    except Exception as e:
        print(f"Lỗi: Hãy chắc chắn bạn đã chạy server trước! ({e})")
