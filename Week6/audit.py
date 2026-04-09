# Kiểm tra bảo mật JWT
# Cài: pip install requests
# Chạy: python audit.py

import requests, base64, json, hmac, hashlib, time

PORT = 3000
BASE = f"http://localhost:{PORT}"

print(f"Kiểm tra server tại {BASE}\n")

# Lấy token hợp lệ
r = requests.post(f"{BASE}/login", json={"username": "admin", "password": "123456"})
token = r.json().get("token") or r.json().get("accessToken")
print(f"Token: {token[:40]}...\n")

# ── Kiểm tra 1: Payload có lộ dữ liệu nhạy cảm? ──────────────────
payload = json.loads(base64.urlsafe_b64decode(token.split(".")[1] + "=="))
print(f"[1] Nội dung payload: {payload}")
bad = [k for k in payload if k in ("password", "pwd", "secret")]
print("    ❌ Có trường nhạy cảm!" if bad else "    ✅ Payload sạch\n")

# ── Kiểm tra 2: Secret có yếu không? ─────────────────────────────
COMMON_SECRETS = ["secret", "123456", "password", "admin",
                  "your_secret_key_here", "khoa_bi_mat_du_manh_123!"]
header_payload = ".".join(token.split(".")[:2]).encode()
real_sig = base64.urlsafe_b64decode(token.split(".")[2] + "==")
cracked = next((s for s in COMMON_SECRETS
                if hmac.new(s.encode(), header_payload, hashlib.sha256).digest() == real_sig), None)
print("[2] Brute-force secret:")
print(f"    ❌ Crack được! Secret là: '{cracked}'" if cracked
      else "    ✅ Secret không nằm trong danh sách phổ biến\n")

# ── Kiểm tra 3: Token hết hạn có bị từ chối? ─────────────────────
expired = ("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
           ".eyJ1c2VyIjoiYWRtaW4iLCJleHAiOjF9"
           ".fake_signature")
r2 = requests.get(f"{BASE}/items", headers={"Authorization": f"Bearer {expired}"})
print(f"[3] Gửi token hết hạn → {r2.status_code}")
print("    ✅ Server từ chối\n" if r2.status_code == 401 else "    ❌ Server vẫn chấp nhận!\n")

# ── Kiểm tra 4: Tấn công alg=none ────────────────────────────────
h = base64.urlsafe_b64encode(b'{"alg":"none","typ":"JWT"}').rstrip(b"=").decode()
p = base64.urlsafe_b64encode(
    json.dumps({"user": "admin", "exp": int(time.time()) + 3600}).encode()
).rstrip(b"=").decode()
r3 = requests.get(f"{BASE}/items", headers={"Authorization": f"Bearer {h}.{p}."})
print(f"[4] Tấn công alg=none → {r3.status_code}")
print("    ✅ Server từ chối\n" if r3.status_code == 401 else "    ❌ Server bị qua mặt!\n")

# ── Kiểm tra 5: Brute force (thử sai mật khẩu nhiều lần) ─────────
print("[5] Thử đăng nhập sai 12 lần liên tiếp:")
for i in range(1, 13):
    r4 = requests.post(f"{BASE}/login", json={"username": "admin", "password": "sai"})
    if r4.status_code == 429:
        print(f"    ✅ Bị chặn sau {i} lần (429 Too Many Requests)\n")
        break
else:
    print("    ❌ Không có giới hạn số lần đăng nhập!\n")
