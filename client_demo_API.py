import requests


def run_final_test():
    BASE_URL = "http://localhost:5000/api/v3/books"

    print("=== BẮT ĐẦU TEST HỆ THỐNG API TỔNG HỢP ===")

    # TEST 1: Tính Nhất quán (V1) & Dễ mở rộng (V3 - Phân trang)
    print("\n[TEST 1] Lấy trang 1 (Mỗi trang 2 cuốn):")
    res1 = requests.get(f"{BASE_URL}?page=1&limit=2")
    d1 = res1.json()
    print(f"  > Cấu trúc chuẩn (V1): {list(d1.keys())}")
    print(f"  > Phân trang (V3): Đang xem trang {d1['metadata']['page']}")
    print(f"  > Dữ liệu: {d1['data']}")

    # TEST 2: Tính Dễ hiểu (V2 - Báo lỗi nhập liệu)
    print("\n[TEST 2] Thử thêm sách nhưng thiếu 'title':")
    res2 = requests.post(BASE_URL, json={"author": "Hưng"})
    d2 = res2.json()
    print(f"  > HTTP Code: {res2.status_code}")
    print(f"  > Thông báo lỗi (V2): {d2['message']}")

    # TEST 3: Tính Dễ hiểu (V2 - Lỗi tham số sai kiểu)
    print("\n[TEST 3] Thử nhập page là chữ thay vì số:")
    res3 = requests.get(f"{BASE_URL}?page=abc")
    print(f"  > HTTP Code: {res3.status_code}")
    print(f"  > Giải thích lỗi (V2): {res3.json()['message']}")


if __name__ == "__main__":
    run_final_test()
