import requests

BASE_URL = "http://localhost:5000/items"
current_api_key = ""


def show_menu():
    global current_api_key
    print(
        f"\n--- DEMO Stateless (Key: {current_api_key if current_api_key else 'Chưa có'}) ---")
    print("0. Nhập API Key (Thiết lập định danh)")
    print("1. Xem danh sách giày (GET /items)")
    print("2. Thêm giày mới (POST /items)")
    print("3. Xóa giày theo ID (DELETE /items/<id>)")
    print("4. Thoát")
    return input("Chọn lệnh: ")


def run_client():
    global current_api_key

    while True:
        choice = show_menu()
        # Header này sẽ mang Key đi trong mỗi Request
        headers = {"X-API-KEY": current_api_key}

        if choice == '0':
            current_api_key = input("Nhập Key của bạn: ")
            print("Đã lưu Key tại phía Client!")

        elif choice == '1':
            response = requests.get(BASE_URL, headers=headers)
            # Kiểm tra xem Server trả về thành công hay lỗi
            if response.status_code == 200:
                print("\n[DANH SÁCH]:", response.json())
            else:
                print("\n[LỖI]:", response.json().get('error'))

        elif choice == '2':
            try:
                id_moi = int(input("Nhập ID: "))
                ten_moi = input("Nhập tên giày: ")
                gia_moi = int(input("Nhập giá: "))
                payload = {"id": id_moi, "name": ten_moi, "price": gia_moi}

                response = requests.post(
                    BASE_URL, json=payload, headers=headers)
                print("\n[SERVER RESPONSE]:", response.json())
            except ValueError:
                print("Lỗi: ID và Giá phải là số!")

        elif choice == '3':
            id_xoa = input("Nhập ID cần xóa: ")
            response = requests.delete(f"{BASE_URL}/{id_xoa}", headers=headers)
            print("\n[SERVER RESPONSE]:", response.json())

        elif choice == '4':
            print("Tạm biệt!")
            break
        else:
            print("Lựa chọn không hợp lệ!")


if __name__ == "__main__":
    run_client()
