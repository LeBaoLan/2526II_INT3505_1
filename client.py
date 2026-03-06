import requests

BASE_URL = "http://localhost:5000/items"


def show_menu():
    print("\n--- DEMO UNIFORM INTERFACE ---")
    print("1. Xem danh sách giày (GET /items)")
    print("2. Thêm giày mới (POST /items)")
    print("3. Xóa giày theo ID (DELETE /items/<id>)")
    print("4. Thoát")
    return input("Chọn lệnh (1-4): ")


def run_client():
    while True:
        choice = show_menu()

        if choice == '1':
            # GET
            response = requests.get(BASE_URL)
            print("\n[SERVER RESPONSE]:", response.json())

        elif choice == '2':
            # POST
            try:
                id_moi = int(input("Nhập ID: "))
                ten_moi = input("Nhập tên giày: ")
                gia_moi = int(input("Nhập giá: "))

                payload = {"id": id_moi, "name": ten_moi, "price": gia_moi}
                response = requests.post(BASE_URL, json=payload)
                print("\n[SERVER RESPONSE]:", response.json())
            except ValueError:
                print("Lỗi: ID và Giá phải là số!")

        elif choice == '3':
            # DELETE
            id_xoa = input("Nhập ID cần xóa: ")
            response = requests.delete(f"{BASE_URL}/{id_xoa}")
            print("\n[SERVER RESPONSE]:", response.json())

        elif choice == '4':
            print("Thoát")
            break
        else:
            print("Lựa chọn không hợp lệ!")


if __name__ == "__main__":
    run_client()
