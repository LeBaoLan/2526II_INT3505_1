# 🛍️ Product API — Flask + MongoDB

## 📁 Cấu trúc thư mục

```
Week7/
├── .env                          # Biến môi trường (không push lên Git)
├── requirements.txt              # Danh sách thư viện Python
├── run.py                        # Entry point — chạy server
├── seed.py                       # Tạo dữ liệu mẫu
└── app/
    ├── __init__.py               # Khởi tạo Flask app + kết nối MongoDB
    ├── models/
    │   └── product.py            # Serializer chuyển đổi dữ liệu
    ├── controllers/
    │   └── product_controller.py # Xử lý logic CRUD
    └── routes/
        └── product_routes.py     # Định nghĩa các route
```

---

## ⚙️ Cài đặt và chạy

### Bước 1: Clone project

```bash
git clone <repo-url>
cd Week7
```

### Bước 2: Tạo môi trường ảo

```bash
python -m venv venv
```

Kích hoạt môi trường ảo:

```bash
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

> Terminal sẽ hiện `(venv)` ở đầu dòng là thành công.

### Bước 3: Cài thư viện

```bash
pip install -r requirements.txt
```

### Bước 4: Tạo file `.env`

Tạo file `.env` ở thư mục gốc, nội dung:

```
PORT=3000
MONGODB_URI=mongodb://localhost:27017/productdb
```

### Bước 5: Đảm bảo MongoDB đang chạy

Mở **MongoDB Compass** → kết nối với:
```
mongodb://localhost:27017
```
Thấy kết nối thành công là MongoDB đang chạy.

### Bước 6: Chạy server

```bash
python run.py
```

Kết quả thành công:
```
* Running on http://127.0.0.1:3000
```

### Bước 7: (Tuỳ chọn) Tạo dữ liệu mẫu

Mở terminal mới (vẫn trong venv), chạy:

```bash
python seed.py
```

Kết quả:
```
🗑️  Đã xóa dữ liệu cũ
🌱 Đã thêm 15 sản phẩm vào database!
```

---

## 🔌 Các API Endpoints

| Method | URL | Chức năng |
|--------|-----|-----------|
| GET | `/api/products` | Lấy tất cả sản phẩm |
| GET | `/api/products/:id` | Lấy 1 sản phẩm theo ID |
| POST | `/api/products` | Tạo sản phẩm mới |
| PUT | `/api/products/:id` | Cập nhật sản phẩm |
| DELETE | `/api/products/:id` | Xóa sản phẩm |

---

## 🧪 Test API bằng Postman

### Tạo sản phẩm mới — `POST /api/products`

- Tab **Body** → **raw** → **JSON**

```json
{
  "name": "Laptop Dell XPS 15",
  "description": "Laptop cao cấp cho lập trình viên",
  "price": 35000000,
  "stock": 10
}
```

### Lấy tất cả sản phẩm — `GET /api/products`

Không cần body, nhấn **Send** là thấy danh sách.

### Lấy 1 sản phẩm — `GET /api/products/{id}`

Thay `{id}` bằng `_id` lấy từ kết quả GET ở trên.

### Cập nhật sản phẩm — `PUT /api/products/{id}`

```json
{
  "price": 32000000,
  "stock": 8
}
```

### Xóa sản phẩm — `DELETE /api/products/{id}`

Không cần body, nhấn **Send** → trả về `"Xóa thành công"`.

---

## ✅ Kiểm tra dữ liệu trên MongoDB Compass

1. Mở **MongoDB Compass**
2. Kết nối: `mongodb://localhost:27017`
3. Vào database **productdb** → collection **products**
4. Thấy dữ liệu thay đổi theo đúng các thao tác API là thành công

---