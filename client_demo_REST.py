import requests
import requests_cache

requests_cache.install_cache('shoe_store_cache', backend='memory')

BASE_URL = "http://localhost:5000"
current_token = ""


def show_menu():
    global current_token
    # Chỉ hiển thị 10 ký tự đầu của Token cho gọn
    display_token = (current_token[:10] + "...") if current_token else "None"
    print(f"\n--- DEMO JWT (Token: {display_token}) ---")
    print("0. Đăng nhập (Lấy JWT)")
    print("1. Xem danh sách giày (Kiểm tra Cache)")
    print("2. Thêm giày mới (POST)")
    print("3. Xóa giày theo ID (DELETE)")
    print("4. Thoát")
    return input("Chọn lệnh: ")


def run_client():
    global current_token
    while True:
        choice = show_menu()
        # Định dạng chuẩn JWT: Bearer <token>
        headers = {"Authorization": f"Bearer {current_token}"}

        if choice == '0':
            user = input("Username: ")
            pwd = input("Password: ")
            res = requests.post(f"{BASE_URL}/login",
                                json={"username": user, "password": pwd})
            if res.status_code == 200:
                current_token = res.json().get('token')
                print("Đăng nhập thành công! Đã lưu Token.")
            else:
                print(f"Thất bại: {res.json().get('error')}")

        elif choice == '1':
            response = requests.get(f"{BASE_URL}/items", headers=headers)

            if response.status_code == 200:
                is_from_cache = getattr(response, 'from_cache', False)
                print(f"[DỮ LIỆU]: {response.json()}")
                print(f"[NGUỒN]: {'CACHE' if is_from_cache else 'SERVER'}")
            else:
                print(
                    f"[LỖI {response.status_code}]: {response.json().get('error')}")

        elif choice == '2':
            payload = {"id": int(input("ID: ")), "name": input(
                "Tên: "), "price": int(input("Giá: "))}
            response = requests.post(
                f"{BASE_URL}/items", json=payload, headers=headers)
            print(f"Response: {response.json()}")
            requests_cache.clear()

        elif choice == '3':
            id_xoa = input("ID cần xóa: ")
            response = requests.delete(
                f"{BASE_URL}/items/{id_xoa}", headers=headers)
            print(f"Response: {response.json()}")
            requests_cache.clear()

        elif choice == '4':
            break


if __name__ == "__main__":
    run_client()
