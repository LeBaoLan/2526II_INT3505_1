# Thiet ke API cho he thong thong bao

## 1. Boi canh bai toan

He thong thong bao cho phep ung dung gui thong bao den nguoi dung qua nhieu kenh như email, SMS, push notification va in-app notification.

Vi day la bai tap, pham vi duoc thiet ke o muc vua du:

- Quan ly nguoi dung nhan thong bao.
- Quan ly mau thong bao.
- Tao va gui thong bao.
- Truy van lich su thong bao.
- Cho phep he thong ben ngoai dang ky webhook de nhan su kien.
- Phat su kien khi thong bao duoc tao, gui thanh cong hoac gui that bai.

## 2. Lua chon kieu API

### REST

REST phu hop cho bai toan nay vi:

- Tai nguyen ro rang: users, notifications, templates, webhook subscriptions.
- CRUD la nhu cau chinh.
- De demo, de test bang Postman/cURL.
- Phu hop voi tich hop webhook.

### gRPC

gRPC co the dung neu he thong gui thong bao can hieu nang cao giua cac microservice noi bo, vi:

- Contract chat che bang protobuf.
- Toc do tot hon REST trong giao tiep service-to-service.
- Phu hop voi streaming hoac goi noi bo tan suat cao.

Trong bai tap nay, REST duoc chon lam API cong khai. gRPC chi duoc de xuat cho giao tiep noi bo neu mo rong he thong.

### GraphQL

GraphQL phu hop neu client can truy van linh hoat, vi du lay nguoi dung kem danh sach thong bao, tuy chinh field tra ve. Tuy nhien bai toan nay chu yeu la lenh gui thong bao va webhook, nen GraphQL khong phai lua chon chinh.

## 3. Mo hinh tai nguyen

### User

```json
{
  "id": "usr_001",
  "email": "user@example.com",
  "phone": "+84901234567",
  "deviceTokens": ["device_token_1"],
  "createdAt": "2026-05-17T09:00:00Z"
}
```

### NotificationTemplate

```json
{
  "id": "tpl_welcome",
  "name": "Welcome message",
  "channel": "email",
  "subject": "Welcome, {{name}}",
  "body": "Hello {{name}}, welcome to our system."
}
```

### Notification

```json
{
  "id": "ntf_001",
  "recipientId": "usr_001",
  "channel": "email",
  "title": "Welcome",
  "content": "Hello An, welcome to our system.",
  "status": "pending",
  "createdAt": "2026-05-17T09:10:00Z",
  "sentAt": null
}
```

### WebhookSubscription

```json
{
  "id": "wh_001",
  "url": "https://partner.example.com/webhooks/notifications",
  "events": ["notification.sent", "notification.failed"],
  "status": "active",
  "secret": "whsec_xxx",
  "createdAt": "2026-05-17T09:15:00Z"
}
```

## 4. CRUD Pattern

CRUD duoc dung cho cac tai nguyen co vong doi ro rang.

### Users

| Method | Endpoint | Y nghia |
| --- | --- | --- |
| POST | `/users` | Tao nguoi dung |
| GET | `/users/{userId}` | Lay thong tin nguoi dung |
| PATCH | `/users/{userId}` | Cap nhat nguoi dung |
| DELETE | `/users/{userId}` | Xoa nguoi dung |

Vi du tao user:

```http
POST /users
Content-Type: application/json

{
  "email": "user@example.com",
  "phone": "+84901234567",
  "deviceTokens": ["device_token_1"]
}
```

### Templates

| Method | Endpoint | Y nghia |
| --- | --- | --- |
| POST | `/notification-templates` | Tao mau thong bao |
| GET | `/notification-templates/{templateId}` | Lay mau thong bao |
| PATCH | `/notification-templates/{templateId}` | Cap nhat mau |
| DELETE | `/notification-templates/{templateId}` | Xoa mau |

### Webhook subscriptions

| Method | Endpoint | Y nghia |
| --- | --- | --- |
| POST | `/webhook-subscriptions` | Dang ky webhook |
| GET | `/webhook-subscriptions/{subscriptionId}` | Xem cau hinh webhook |
| PATCH | `/webhook-subscriptions/{subscriptionId}` | Cap nhat URL/events/status |
| DELETE | `/webhook-subscriptions/{subscriptionId}` | Huy webhook |

## 5. Query Pattern

Query pattern dung khi client can loc, sap xep, phan trang.

### Lay danh sach thong bao

```http
GET /notifications?recipientId=usr_001&status=sent&channel=email&page=1&pageSize=20
```

Response:

```json
{
  "data": [
    {
      "id": "ntf_001",
      "recipientId": "usr_001",
      "channel": "email",
      "title": "Welcome",
      "status": "sent",
      "createdAt": "2026-05-17T09:10:00Z",
      "sentAt": "2026-05-17T09:10:05Z"
    }
  ],
  "pagination": {
    "page": 1,
    "pageSize": 20,
    "total": 1
  }
}
```

Mot so query huu ich:

| Endpoint | Muc dich |
| --- | --- |
| `/notifications?status=pending` | Lay thong bao dang cho gui |
| `/notifications?status=failed` | Lay thong bao gui loi |
| `/notifications?recipientId=usr_001` | Lay lich su thong bao cua mot user |
| `/notifications?from=2026-05-01&to=2026-05-17` | Loc theo khoang thoi gian |

## 6. HATEOAS Pattern

HATEOAS giup response chua cac link hanh dong tiep theo, lam API tu mo ta hon.

Vi du response khi lay mot thong bao:

```json
{
  "id": "ntf_001",
  "recipientId": "usr_001",
  "channel": "email",
  "title": "Welcome",
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

Neu notification dang `sent`, link `retry` co the khong xuat hien. Cach nay giup client biet hanh dong nao hop le theo trang thai hien tai.

## 7. Command endpoint cho viec gui thong bao

Gui thong bao la hanh dong nghiep vu, khong chi la CRUD thong thuong.

### Gui thong bao truc tiep

```http
POST /notifications
Content-Type: application/json

{
  "recipientId": "usr_001",
  "channel": "email",
  "title": "Welcome",
  "content": "Hello An, welcome to our system."
}
```

Response:

```json
{
  "id": "ntf_001",
  "status": "pending",
  "_links": {
    "self": {
      "href": "/notifications/ntf_001"
    }
  }
}
```

### Gui thong bao tu template

```http
POST /notifications
Content-Type: application/json

{
  "recipientId": "usr_001",
  "templateId": "tpl_welcome",
  "variables": {
    "name": "An"
  }
}
```

### Gui lai thong bao loi

```http
POST /notifications/ntf_001/retry
```

## 8. Event-driven Pattern

He thong nen phat su kien khi trang thai thong bao thay doi.

### Cac su kien chinh

| Event | Khi nao phat sinh |
| --- | --- |
| `notification.created` | Khi notification duoc tao |
| `notification.sent` | Khi gui thanh cong |
| `notification.failed` | Khi gui that bai |
| `notification.read` | Khi user doc thong bao in-app |

### Event payload noi bo

```json
{
  "id": "evt_001",
  "type": "notification.sent",
  "occurredAt": "2026-05-17T09:10:05Z",
  "data": {
    "notificationId": "ntf_001",
    "recipientId": "usr_001",
    "channel": "email",
    "status": "sent"
  }
}
```

### Luong xu ly

1. Client goi `POST /notifications`.
2. API tao notification voi status `pending`.
3. Notification service dua job vao queue.
4. Worker gui email/SMS/push.
5. Worker cap nhat status thanh `sent` hoac `failed`.
6. He thong phat event tuong ung.
7. Webhook dispatcher gui event den cac webhook da dang ky.

## 9. Webhook Pattern

Webhook dung de he thong ben ngoai nhan thong bao khi co su kien ma khong can lien tuc polling API.

### Dang ky webhook

```http
POST /webhook-subscriptions
Content-Type: application/json

{
  "url": "https://partner.example.com/webhooks/notifications",
  "events": ["notification.sent", "notification.failed"]
}
```

Response:

```json
{
  "id": "wh_001",
  "url": "https://partner.example.com/webhooks/notifications",
  "events": ["notification.sent", "notification.failed"],
  "status": "active",
  "secret": "whsec_123",
  "_links": {
    "self": {
      "href": "/webhook-subscriptions/wh_001"
    },
    "test": {
      "href": "/webhook-subscriptions/wh_001/test",
      "method": "POST"
    }
  }
}
```

### Payload gui den webhook

```http
POST https://partner.example.com/webhooks/notifications
Content-Type: application/json
X-Webhook-Event: notification.sent
X-Webhook-Delivery: dlv_001
X-Webhook-Timestamp: 1778999405
X-Webhook-Signature: sha256=...

{
  "id": "evt_001",
  "type": "notification.sent",
  "occurredAt": "2026-05-17T09:10:05Z",
  "data": {
    "notificationId": "ntf_001",
    "recipientId": "usr_001",
    "channel": "email",
    "status": "sent"
  }
}
```

### Bao mat webhook

Webhook nen co chu ky de ben nhan xac minh request that su den tu he thong thong bao.

Cong thuc:

```text
signature = HMAC_SHA256(secret, timestamp + "." + raw_body)
```

Ben nhan webhook can:

1. Lay `X-Webhook-Timestamp`.
2. Lay raw request body.
3. Tinh lai HMAC bang webhook secret.
4. So sanh voi `X-Webhook-Signature`.
5. Tu choi request neu timestamp qua cu, vi du qua 5 phut.

### Retry webhook

Neu webhook endpoint tra ve loi `5xx` hoac timeout, he thong nen retry:

| Lan thu | Thoi gian retry |
| --- | --- |
| 1 | Sau 1 phut |
| 2 | Sau 5 phut |
| 3 | Sau 30 phut |

Neu endpoint tra ve `2xx`, xem nhu thanh cong. Neu tra ve `4xx`, co the khong retry vi thuong la loi cau hinh cua ben nhan.

### Idempotency

Moi lan giao webhook co `X-Webhook-Delivery`. Ben nhan nen luu delivery id da xu ly de tranh xu ly trung khi he thong retry.

## 10. API errors

Dung format loi thong nhat:

```json
{
  "error": {
    "code": "INVALID_WEBHOOK_URL",
    "message": "Webhook URL must use HTTPS.",
    "details": {
      "field": "url"
    }
  }
}
```

Mot so ma loi:

| HTTP status | Code | Y nghia |
| --- | --- | --- |
| 400 | `VALIDATION_ERROR` | Du lieu dau vao khong hop le |
| 401 | `UNAUTHORIZED` | Thieu hoac sai API key |
| 403 | `FORBIDDEN` | Khong co quyen |
| 404 | `NOT_FOUND` | Khong tim thay tai nguyen |
| 409 | `CONFLICT` | Xung dot trang thai, vi du retry notification da sent |
| 429 | `RATE_LIMITED` | Goi API qua nhieu |
| 500 | `INTERNAL_ERROR` | Loi he thong |

## 11. Idempotency cho API tao notification

Khi client tao notification, co the gui header:

```http
Idempotency-Key: req_abc_123
```

Neu client retry cung request do loi mang, server tra ve cung mot notification da tao truoc do thay vi tao trung.

Pattern nay giong cach cac API thanh toan nhu Stripe thiet ke de tranh lap giao dich.

## 12. Phan tich API Stripe va GitHub

### Stripe

Mot so pattern de hoc tu Stripe:

- REST resource ro rang: customers, payment intents, checkout sessions, events.
- Dung idempotency key cho request tao tai nguyen quan trong.
- Webhook la thanh phan trung tam de bao su kien bat dong bo.
- Event co `type` va `data`, giup client xu ly theo tung loai su kien.
- Co chu ky webhook de xac minh nguon gui.
- API errors co cau truc nhat quan.

Ap dung vao he thong thong bao:

- Dung `Idempotency-Key` khi tao notification.
- Dung `event.type` cho webhook như `notification.sent`.
- Ky webhook bang secret rieng cho tung subscription.
- Co retry webhook neu delivery that bai.

### GitHub

Mot so pattern de hoc tu GitHub:

- REST API dung resource ro rang: repos, issues, pulls, hooks.
- Webhook cho phep chon event can nhan.
- Header webhook co event name va delivery id.
- Delivery id giup debug va xu ly idempotency.
- HATEOAS/link headers duoc dung trong pagination va dieu huong.

Ap dung vao he thong thong bao:

- Cho client dang ky webhook voi danh sach event mong muon.
- Them `X-Webhook-Event` va `X-Webhook-Delivery`.
- Luu lich su delivery de debug webhook.
- Dung pagination cho danh sach notification va event.

## 13. Tom tat pattern da su dung

| Pattern | Ap dung trong he thong |
| --- | --- |
| CRUD | Users, templates, webhook subscriptions |
| Query | Loc danh sach notification theo user, status, channel, thoi gian |
| HATEOAS | Response co `_links` den self, retry, recipient, webhook events |
| Event-driven | Phat event khi notification created/sent/failed/read |
| Webhook | Gui event den he thong ben ngoai |
| Idempotency | Tranh tao trung notification khi retry request |

## 14. Ket luan

He thong thong bao phu hop voi REST API ket hop nhieu design patterns. CRUD giup quan ly tai nguyen, query giup truy van linh hoat, HATEOAS giup client biet hanh dong tiep theo, event-driven giup xu ly bat dong bo, va webhook giup tich hop voi he thong ben ngoai. Neu he thong lon hon, co the bo sung gRPC cho giao tiep noi bo va GraphQL cho client can truy van du lieu phuc tap.
