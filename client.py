import requests


def display_store():
    url = "http://localhost:5000/items"
    try:
        response = requests.get(url)
        data = response.json()

        print("=== CỬA HÀNG GIÀY ===")
        for item in data:
            print(
                f"ID: {item['id']} | Tên: {item['name']} | Giá: {item['price']}k")
        print("==============================")

    except Exception as e:
        print(f"Không thể kết nối tới Server: {e}")


if __name__ == "__main__":
    display_store()
