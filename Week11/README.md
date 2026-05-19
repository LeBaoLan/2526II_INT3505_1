# Notification API Demo

Demo Flask cho bài tập API Design Patterns. Hệ thống mô phỏng dịch vụ thông báo có REST API, CRUD, Query, HATEOAS, Event-driven và Webhook.

## 1. Yêu cầu

- Python 3.10 trở lên.
- Flask.
- Postman để test API.

## 2. Cài đặt

Tạo virtual environment:

```powershell
python -m venv .venv
```

Kích hoạt virtual environment trên Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Cài thư viện:

```powershell
pip install -r requirements.txt
```

## 3. Chạy server

Chạy Notification API:

```powershell
python app.py
```

Mặc định API chạy tại:

```text
http://127.0.0.1:3000
```

Chạy webhook receiver local ở terminal thứ hai:

```powershell
python webhook_receiver.py
```

Receiver local chạy tại:

```text
http://127.0.0.1:4000/webhooks/notifications
```

## 4. Chạy như server có thể nhận/gửi qua URL thật

Demo này gửi webhook bằng HTTP request thật. Có 2 cách demo:

### Cách A: Dùng webhook.site

1. Mở [https://webhook.site](https://webhook.site).
2. Copy URL riêng mà trang tạo cho bạn, ví dụ:

```text
https://webhook.site/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

3. Dùng URL đó làm `url` khi tạo webhook subscription trong Postman.
4. Khi notification chuyển sang `sent` hoặc `failed`, request webhook sẽ hiện trực tiếp trên webhook.site.

Cách này dễ nhất để chứng minh hệ thống có gọi webhook URL public thật.

### Cách B: Dùng ngrok để public webhook receiver local

Nếu muốn dùng chính `webhook_receiver.py` nhưng có URL public:

```powershell
python webhook_receiver.py
```

Sau đó mở terminal khác:

```powershell
ngrok http 4000
```

Ngrok sẽ cấp URL dạng:

```text
https://abc123.ngrok-free.app
```

Webhook URL cần đăng ký là:

```text
https://abc123.ngrok-free.app/webhooks/notifications
```

Nếu muốn API Flask lắng nghe bên ngoài localhost:

```powershell
$env:APP_HOST="0.0.0.0"
$env:APP_PORT="3000"
python app.py
```

## 5. Dữ liệu mẫu

Khi khởi động, API tự tạo:

| Resource | ID |
| --- | --- |
| User mẫu | `usr_001` |
| Template mẫu | `tpl_001` |

## 6. Test bằng Postman

Tạo environment trong Postman:

| Variable | Initial value |
| --- | --- |
| `base_url` | `http://127.0.0.1:3000` |
| `webhook_url` | URL từ webhook.site, ngrok, hoặc `http://127.0.0.1:4000/webhooks/notifications` |

Bạn có thể import sẵn collection này vào Postman:

```text
postman_collection.json
```

Với các request có body, chọn:

- Tab `Body`.
- Chọn `raw`.
- Chọn `JSON`.

## 7. Các request nên tạo trong Postman

### Health check

Method:

```text
GET
```

URL:

```text
{{base_url}}/health
```

### Tạo user

Method:

```text
POST
```

URL:

```text
{{base_url}}/users
```

Body:

```json
{
  "email": "student@example.com",
  "phone": "+84901234567",
  "deviceTokens": ["device_1"]
}
```

### Lấy danh sách user

Method:

```text
GET
```

URL:

```text
{{base_url}}/users
```

### Tạo template

Method:

```text
POST
```

URL:

```text
{{base_url}}/notification-templates
```

Body:

```json
{
  "name": "Payment success",
  "channel": "email",
  "subject": "Payment {{orderId}}",
  "body": "Your order {{orderId}} was paid successfully."
}
```

### Tạo webhook subscription

Method:

```text
POST
```

URL:

```text
{{base_url}}/webhook-subscriptions
```

Body:

```json
{
  "url": "{{webhook_url}}",
  "events": ["notification.sent", "notification.failed"]
}
```

Response sẽ có `secret`. Nếu dùng `webhook_receiver.py` và muốn xác minh chữ ký, copy secret đó rồi chạy receiver với biến môi trường:

```powershell
$env:WEBHOOK_SECRET="whsec_xxx"
python webhook_receiver.py
```

Nếu dùng webhook.site thì không cần bước này, vì webhook.site chỉ dùng để xem request được gửi đến.

### Gửi notification trực tiếp

Method:

```text
POST
```

URL:

```text
{{base_url}}/notifications
```

Headers:

| Key | Value |
| --- | --- |
| `Idempotency-Key` | `demo-request-001` |

Body:

```json
{
  "recipientId": "usr_001",
  "channel": "email",
  "title": "Webhook demo",
  "content": "This should trigger webhook"
}
```

Kết quả:

- API trả về notification với status ban đầu là `pending`.
- Sau khoảng 300ms, notification chuyển sang `sent`.
- Hệ thống gửi webhook thật đến URL đã đăng ký.

### Gửi notification bằng template

Method:

```text
POST
```

URL:

```text
{{base_url}}/notifications
```

Body:

```json
{
  "recipientId": "usr_001",
  "templateId": "tpl_001",
  "variables": {
    "name": "An"
  }
}
```

### Query notification

Method:

```text
GET
```

URL:

```text
{{base_url}}/notifications?recipientId=usr_001&status=sent&page=1&pageSize=10
```

### Tạo notification lỗi để test retry

Method:

```text
POST
```

URL:

```text
{{base_url}}/notifications
```

Body:

```json
{
  "recipientId": "usr_001",
  "channel": "email",
  "title": "fail demo",
  "content": "This message will fail"
}
```

Notification có `fail` hoặc `error` trong title/content sẽ lỗi ở lần gửi đầu tiên. Đợi khoảng 1 giây, lấy ID trả về, ví dụ `ntf_004`, rồi retry.

### Retry notification lỗi

Method:

```text
POST
```

URL:

```text
{{base_url}}/notifications/ntf_004/retry
```

Thay `ntf_004` bằng ID thật mà Postman trả về. Retry chỉ hợp lệ khi notification đang ở trạng thái `failed`.

### Xem event

Method:

```text
GET
```

URL:

```text
{{base_url}}/events
```

### Xem webhook deliveries

Method:

```text
GET
```

URL:

```text
{{base_url}}/webhook-deliveries
```

Endpoint này giúp kiểm tra hệ thống đã gửi webhook chưa, gửi đến event nào, trạng thái delivery là `succeeded` hay `failed`.

## 8. Webhook hoạt động như thế nào

Khi gọi `POST /notifications`, hệ thống xử lý:

1. Tạo notification với trạng thái `pending`.
2. Phát event `notification.created`.
3. Worker giả lập gửi notification sau khoảng 300ms.
4. Nếu thành công, trạng thái đổi thành `sent` và phát `notification.sent`.
5. Nếu title/content chứa `fail` hoặc `error`, lần gửi đầu tiên đổi thành `failed` và phát `notification.failed`.
6. Webhook dispatcher gửi HTTP `POST` thật đến URL trong webhook subscription.

Webhook request có các header:

| Header | Ý nghĩa |
| --- | --- |
| `X-Webhook-Event` | Loại event, ví dụ `notification.sent` |
| `X-Webhook-Delivery` | ID duy nhất của lần gửi webhook |
| `X-Webhook-Timestamp` | Unix timestamp lúc gửi |
| `X-Webhook-Signature` | Chữ ký HMAC SHA-256 |

Cách ký:

```text
signature = HMAC_SHA256(secret, timestamp + "." + raw_body)
```

## 9. HATEOAS

Response notification có `_links`, ví dụ:

```json
{
  "id": "ntf_001",
  "status": "failed",
  "_links": {
    "self": {
      "href": "/notifications/ntf_001"
    },
    "recipient": {
      "href": "/users/usr_001"
    },
    "retry": {
      "href": "/notifications/ntf_001/retry",
      "method": "POST"
    },
    "webhookEvents": {
      "href": "/notifications/ntf_001/events"
    }
  }
}
```

Nếu notification không ở trạng thái `failed`, link `retry` sẽ không xuất hiện.

## 10. Pattern đã thể hiện

| Pattern | Nơi thể hiện |
| --- | --- |
| CRUD | `/users`, `/notification-templates`, `/webhook-subscriptions` |
| Query | `GET /notifications?recipientId=&status=&channel=&page=&pageSize=` |
| HATEOAS | `_links` trong response notification và webhook subscription |
| Event-driven | `notification.created`, `notification.sent`, `notification.failed` |
| Webhook | Gửi HTTP request thật đến webhook URL đã đăng ký |
| Idempotency | Header `Idempotency-Key` khi tạo notification |
