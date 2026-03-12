import requests


def test_api():
    test_cases = [
        ("GET tất cả sách", "GET", "http://localhost:5000/api/books", None),
        ("GET sách sai ID", "GET", "http://localhost:5000/api/books/99", None),
        ("POST thiếu title", "POST",
         "http://localhost:5000/api/books", {"author": "Hưng"}),
    ]

    for desc, method, url, payload in test_cases:
        print(f"Hành động: {desc}")
        if method == "GET":
            res = requests.get(url)
        else:
            res = requests.post(url, json=payload)

        data = res.json()

        # Kiểm tra tính Nhất quán (V1)
        print(f"  > Status: {data['status']}")
        # Kiểm tra tính Dễ hiểu (V2)
        print(f"  > HTTP Code: {res.status_code}")
        if 'message' in data:
            print(f"  > Thông báo: {data['message']}")
        print("-" * 30)


if __name__ == "__main__":
    test_api()
