import requests
import requests_cache
import time

# Thiết lập Cache: Lưu trong bộ nhớ (memory)
# requests_cache sẽ tự động đọc header 'Cache-Control' từ Server để quyết định thời gian lưu
requests_cache.install_cache('shoe_store_cache', backend='memory')

BASE_URL = "http://localhost:5000/items"
current_api_key = ""


def show_menu():
    global current_api_key
    print(
        f"\n--- DEMO V4 CACHEABLE & STATELESS (Key: {current_api_key if current_api_key else 'None'}) ---")
    print("0. Nhập API Key")
    print("1. Xem danh sách giày (Kiểm tra Cache)")
    print("2. Thêm giày mới (POST)")
    print("3. Xóa giày theo ID (DELETE)")
    print("4. Thoát")
    return input("Chọn lệnh: ")


def run_client():
    global current_api_key
    while True:
        choice = show_menu()
        headers = {"X-API-KEY": current_api_key}

        if choice == '0':
            current_api_key = input("Nhập Key: ")
            print("Đã cập nhật Key tại Client.")

        elif choice == '1':
            start_time = time.time()
            response = requests.get(BASE_URL, headers=headers)
            end_time = time.time()

            print(f"Mã trạng thái (Status Code): {response.status_code}")

            if response.status_code == 200:
                is_from_cache = getattr(response, 'from_cache', False)
                print(f"[DỮ LIỆU]: {response.json()}")
                print(f"[THỜI GIAN]: {end_time - start_time:.6f} giây")
                print(
                    f"[NGUỒN]: {'TỪ CACHE (Nhanh)' if is_from_cache else 'TỪ SERVER (Chậm)'}")
            else:
                print(
                    f"[LỖI]: {response.json().get('error', 'Lỗi không xác định')}")

        elif choice == '2':
            try:
                id_moi = int(input("Nhập ID: "))
                ten_moi = input("Nhập tên giày: ")
                gia_moi = int(input("Nhập giá: "))
                payload = {"id": id_moi, "name": ten_moi, "price": gia_moi}

                response = requests.post(
                    BASE_URL, json=payload, headers=headers)
                print(f"Mã trạng thái: {response.status_code}")
                print(f"[SERVER RESPONSE]: {response.json()}")

                # Xóa cache sau khi thêm mới để đảm bảo lần xem sau sẽ lấy dữ liệu mới nhất
                requests_cache.clear()
            except ValueError:
                print("Lỗi: ID và Giá phải là số!")

        elif choice == '3':
            id_xoa = input("Nhập ID cần xóa: ")
            response = requests.delete(f"{BASE_URL}/{id_xoa}", headers=headers)
            print(f"Mã trạng thái: {response.status_code}")
            print(f"[SERVER RESPONSE]: {response.json()}")

            # Xóa cache sau khi xóa dữ liệu
            requests_cache.clear()

        elif choice == '4':
            print("Thoát!")
            break
        else:
            print("Lựa chọn không hợp lệ!")


if __name__ == "__main__":
    run_client()

# Cách kiểm chứng nguyên tắc Cacheable:
# Lần đầu bấm phím 1: Thời gian phản hồi sẽ lâu hơn (ví dụ: 0.015s) và nguồn là TỪ SERVER.

# Bấm phím 1 lần nữa ngay lập tức: Thời gian phản hồi sẽ cực nhanh (ví dụ: 0.0001s) và nguồn là TỪ CACHE.

# Đợi sau 30 giây rồi bấm phím 1: Cache hết hạn, Client sẽ lại phải hỏi Server, nguồn trở lại là TỪ SERVER.
