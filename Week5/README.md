# Library Management API

Demo minh họa **Data Modeling** và **Resource Design** — Buổi 5.  
Xây dựng bằng **FastAPI + SQLite**, không cần cài database ngoài.

---

## Yêu cầu

- Python 3.10 trở lên
- pip

---

## Cài đặt

```bash
pip install -r requirements.txt
```

---

## Chạy server

```bash
uvicorn main:app --reload
```

Mở trình duyệt vào `http://localhost:8000/docs` để xem toàn bộ API.

Server tự tạo **10 cuốn sách demo** khi khởi động lần đầu.

---

## Mở API trong Postman

### Bước 1 — Tạo Environment

1. Mở Postman → bấm **Environments** (thanh trái) → bấm **+**
2. Đặt tên `Local`
3. Thêm variable:

| Variable | Initial Value | Current Value |
|---|---|---|
| `baseUrl` | `http://127.0.0.1:8000` | `http://127.0.0.1:8000` |

4. Bấm **Save**
5. Góc trên phải Postman — chọn environment **Local** (mặc định là `No environment`)

### Bước 2 — Import toàn bộ API

FastAPI tự sinh file mô tả API, Postman đọc được trực tiếp:

1. Postman → bấm **Import**
2. Chọn tab **Link**
3. Dán vào: `http://127.0.0.1:8000/openapi.json`
4. Bấm **Continue** → **Import**

Postman tự tạo collection với đầy đủ tất cả endpoint, params, và ví dụ response.

### Bước 3 — Gọi thử API đầu tiên

1. Mở collection vừa import → bấm **GET /books**
2. Vào tab **Params** — bỏ tick hết các param có sẵn (Postman tự điền giá trị `"string"` gây lỗi)
3. Bấm **Send**
4. Response trả về danh sách 10 cuốn sách — lấy `id` bất kỳ để dùng cho các endpoint khác

---

## Cấu trúc file

```
main.py          ← toàn bộ API
seed_large.py    ← tạo 1 triệu bản ghi để benchmark
requirements.txt
README.md
```

---

## Data Model

```
BOOK ──< BOOK_COPY ──< LOAN >── MEMBER
 │
 ├──< AUTHOR   (many-to-many)
 └──< CATEGORY (many-to-many)
```

| Bảng | Vai trò |
|---|---|
| `books` | Đầu sách (title, isbn, năm) |
| `book_copies` | Bản sao vật lý — 1 đầu sách có nhiều bản |
| `authors` | Tác giả — nhiều-nhiều với sách |
| `categories` | Thể loại — nhiều-nhiều với sách |
| `members` | Thành viên thư viện |
| `loans` | Lượt mượn — ai mượn bản nào, khi nào |

---

## Các endpoint

### Books — CRUD

| Method | URL | Mô tả |
|---|---|---|
| GET | `/books` | Danh sách + tìm kiếm + phân trang offset/limit |
| GET | `/books/cursor` | Danh sách với cursor pagination |
| GET | `/books/page` | Danh sách với page-based pagination |
| GET | `/books/{id}` | Chi tiết 1 cuốn sách |
| POST | `/books` | Tạo sách mới |
| PUT | `/books/{id}` | Cập nhật sách |
| DELETE | `/books/{id}` | Xoá sách |

### Members

| Method | URL | Mô tả |
|---|---|---|
| GET | `/members/{id}/loans` | Lịch sử mượn của thành viên |

### Benchmark

| Method | URL | Mô tả |
|---|---|---|
| GET | `/bench/offset` | Test hiệu năng offset trên 1 triệu bản ghi |
| GET | `/bench/cursor` | Test hiệu năng cursor trên 1 triệu bản ghi |
| GET | `/bench/stats` | Kiểm tra số bản ghi đã seed |

---

## Query params phổ biến

**Tìm kiếm và lọc** (dùng được ở `/books`, `/books/page`):

| Param | Ví dụ | Mô tả |
|---|---|---|
| `q` | `q=python` | Tìm theo tên sách hoặc tác giả |
| `author` | `author=martin` | Lọc theo tên tác giả |
| `category` | `category=design` | Lọc theo thể loại |
| `year_from` | `year_from=2000` | Năm xuất bản từ |
| `year_to` | `year_to=2020` | Năm xuất bản đến |
| `available` | `available=true` | Chỉ sách còn bản mượn |
| `sort_by` | `sort_by=published_year` | Sắp xếp theo field |
| `order` | `order=desc` | Thứ tự asc / desc |

---

## Tạo 1 triệu bản ghi để benchmark

> Chỉ cần chạy **1 lần**. Mất khoảng 2–3 phút.  
> Dữ liệu được lưu vào bảng `books_bench` riêng, không ảnh hưởng data demo.

```bash
python seed_large.py
```

Terminal hiển thị tiến độ từng 10,000 bản ghi:

```
Bat dau tao 1,000,000 ban ghi (batch=10,000)...
      10,000 / 1,000,000  (1.0%)  2.1s
      20,000 / 1,000,000  (2.0%)  4.2s
  ...
Xong! Tong: 1,000,000 ban ghi trong 142.3s
```

Sau khi seed xong, restart server:

```bash
uvicorn main:app --reload
```

Kiểm tra data đã có chưa:

```
GET http://localhost:8000/bench/stats
```

---

## Demo so sánh Offset vs Cursor

Sau khi có 1 triệu bản ghi, test theo thứ tự sau trong Postman.  
Nhìn vào **`query_ms`** trong response và **thời gian hiển thị trên thanh Postman**.

### Offset — càng về cuối càng chậm

```
GET /bench/offset?offset=0&limit=10        ← trang đầu     ~2ms
GET /bench/offset?offset=100000&limit=10   ← trang 10k     ~80ms
GET /bench/offset?offset=500000&limit=10   ← trang giữa    ~300ms
GET /bench/offset?offset=900000&limit=10   ← gần cuối      ~600ms
```

### Cursor — luôn ổn định dù ở trang nào

```
# Bước 1 — lấy trang đầu, copy next_cursor từ response
GET /bench/cursor?limit=10

# Bước 2 — dán next_cursor vào, lấy trang tiếp
GET /bench/cursor?cursor=<next_cursor>&limit=10

# Bước 3 — tiếp tục dán next_cursor mới...
# → query_ms luôn ~20ms dù đang ở trang nào
```

### Kết quả kỳ vọng

| Vị trí | Offset | Cursor |
|---|---|---|
| Trang đầu (offset=0) | ~2ms | ~2ms |
| Trang giữa (offset=500k) | ~300–500ms | ~2ms |
| Gần cuối (offset=900k) | ~600ms+ | ~2ms |

**Lý do:** Offset bắt buộc DB đọc và bỏ qua N bản ghi trước khi lấy kết quả.  
Cursor dùng index `WHERE id > cursor` — nhảy thẳng đến điểm cần lấy.

---

## Tạo sách mới (POST)

Dùng Postman, chọn Body → raw → JSON:

```json
{
  "title": "FastAPI in Action",
  "isbn": "978-1234567890",
  "published_year": 2024,
  "author_names": ["Bill Lubanovic"],
  "category_names": ["Python", "Web Development"]
}
```

`author_names` và `category_names` tự động tạo mới nếu chưa tồn tại.

---

## Reset data

Xoá database và tạo lại từ đầu (mất data benchmark):

```bash
# Windows
del library.db

# Mac / Linux
rm library.db

uvicorn main:app --reload
```