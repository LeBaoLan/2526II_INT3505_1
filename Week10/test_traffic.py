"""
Script test: tạo traffic giả lập để quan sát logging & metrics
Chạy song song với app.py
"""
import requests
import time
import random

BASE_URL = "http://localhost:5000"

ENDPOINTS = [
    ("/",        "GET", 3),
    ("/users",   "GET", 4),
    ("/orders",  "GET", 3),
    ("/slow",    "GET", 1),
    ("/error",   "GET", 2),
    ("/health",  "GET", 5),
]

def send_requests(n=20):
    print(f"🚀 Gửi {n} requests ngẫu nhiên tới {BASE_URL}\n")
    for i in range(n):
        endpoint, method, _ = random.choices(ENDPOINTS, weights=[w for _, _, w in ENDPOINTS])[0]
        try:
            resp = requests.request(method, BASE_URL + endpoint, timeout=5)
            print(f"[{i+1:02d}] {method} {endpoint} → {resp.status_code}")
        except Exception as e:
            print(f"[{i+1:02d}] Lỗi kết nối: {e}")
        time.sleep(random.uniform(0.1, 0.5))

    print("\n✅ Xong! Kiểm tra:")
    print(f"  - Logs console bên app.py")
    print(f"  - File logs/app.log và logs/errors.log")
    print(f"  - Prometheus metrics: {BASE_URL}/metrics")

if __name__ == "__main__":
    send_requests(20)
