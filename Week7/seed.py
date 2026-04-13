from pymongo import MongoClient
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

client = MongoClient(os.getenv("MONGODB_URI"))
db = client["productdb"]

products = [
    {"name": "Laptop Dell XPS 15", "description": "Laptop cao cấp cho lập trình viên, màn hình OLED 4K",
        "price": 35000000, "stock": 10},
    {"name": "Laptop MacBook Pro M3 14 inch",
        "description": "Chip Apple M3, pin 18 tiếng, màn hình Liquid Retina", "price": 52000000, "stock": 8},
    {"name": "Laptop ASUS ROG Strix G16",
        "description": "Laptop gaming, RTX 4070, màn hình 165Hz", "price": 42000000, "stock": 15},
    {"name": "Laptop Lenovo ThinkPad X1 Carbon",
        "description": "Laptop doanh nhân siêu nhẹ, bàn phím tốt nhất phân khúc", "price": 38000000, "stock": 6},
    {"name": "iPhone 15 Pro Max 256GB",
        "description": "Chip A17 Pro, camera 48MP, khung titan", "price": 34000000, "stock": 20},
    {"name": "Samsung Galaxy S24 Ultra",
        "description": "Màn hình Dynamic AMOLED, bút S Pen, camera 200MP", "price": 31000000, "stock": 18},
    {"name": "Google Pixel 8 Pro", "description": "AI camera tốt nhất Android, 7 năm cập nhật",
        "price": 23000000, "stock": 9},
    {"name": "Xiaomi 14 Ultra", "description": "Camera Leica, sạc nhanh 90W, Snapdragon 8 Gen 3",
        "price": 20000000, "stock": 25},
    {"name": "Sony WH-1000XM5", "description": "Chống ồn hàng đầu thế giới, pin 30 tiếng",
        "price": 8500000, "stock": 30},
    {"name": "Apple AirPods Pro 2", "description": "Chống ồn ANC, âm thanh không gian, chip H2",
        "price": 6500000, "stock": 22},
    {"name": "Bose QuietComfort 45", "description": "Chống ồn xuất sắc, đệm tai cực êm",
        "price": 7200000, "stock": 17},
    {"name": "Màn hình LG UltraWide 34 inch",
        "description": "Ultrawide 21:9, IPS, 144Hz, HDR400", "price": 12000000, "stock": 7},
    {"name": "Màn hình Dell UltraSharp U2723D",
        "description": "4K IPS, màu sắc chuyên nghiệp, USB-C 90W", "price": 14500000, "stock": 5},
    {"name": "Bàn phím cơ Keychron K2 Pro",
        "description": "75% layout, switch Gateron, Bluetooth + USB-C", "price": 2800000, "stock": 50},
    {"name": "Chuột Logitech MX Master 3S",
        "description": "Chuột không dây cao cấp, cuộn MagSpeed, 8000 DPI", "price": 2500000, "stock": 45},
]

# Thêm timestamp cho mỗi sản phẩm
now = datetime.utcnow()
for p in products:
    p["createdAt"] = now
    p["updatedAt"] = now

db.products.delete_many({})
print("🗑️  Đã xóa dữ liệu cũ")

db.products.insert_many(products)
print(f"🌱 Đã thêm {len(products)} sản phẩm vào database!")

client.close()
