"""
Script test: giả lập traffic bình thường + spam để trigger rate limit
"""
import time
import random

try:
    import requests
except ImportError:
    print("Cai dat requests: pip install requests")
    exit(1)

BASE = "http://localhost:5000"


def req(method, path, label=""):
    try:
        r = requests.request(method, BASE + path, timeout=5)
        icon = "OK " if r.status_code < 400 else (
            "429" if r.status_code == 429 else "ERR")
        print(f"  [{icon}] {method} {path} -> {r.status_code}  {label}")
        return r.status_code
    except Exception as e:
        print(f"  [---] Loi ket noi: {e}")
        return 0


print("=" * 55)
print("TEST 1: Traffic binh thuong")
print("=" * 55)
for ep in ["/", "/health", "/users", "/products", "/users", "/error"]:
    req("GET", ep)
    time.sleep(0.2)

print()
print("=" * 55)
print("TEST 2: Spam /users (gioi han 5/phut) -> phai thay 429")
print("=" * 55)
for i in range(8):
    code = req("GET", "/users", f"(lan {i+1})")
    time.sleep(0.1)

print()
print("=" * 55)
print("TEST 3: Spam /slow (gioi han 3/phut) -> phai thay 429")
print("=" * 55)
for i in range(5):
    code = req("GET", "/slow", f"(lan {i+1})")
    time.sleep(0.05)

print()
print("=" * 55)
print("TEST 4: /health khong bi rate limit")
print("=" * 55)
for i in range(5):
    req("GET", "/health", f"(lan {i+1})")

print()
print("Ket qua metrics tai: http://localhost:5000/metrics")
print("Tim dong: http_rate_limit_exceeded_total")
