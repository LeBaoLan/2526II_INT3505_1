from __future__ import annotations

import hashlib
import hmac
import json
import os
import re
import threading
import time
from datetime import datetime, timezone
from itertools import count
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from flask import Flask, jsonify, make_response, request


app = Flask(__name__)

APP_HOST = os.getenv("APP_HOST", "127.0.0.1")
APP_PORT = int(os.getenv("APP_PORT", "3000"))
WEBHOOK_TIMEOUT_SECONDS = int(os.getenv("WEBHOOK_TIMEOUT_SECONDS", "5"))

db = {
    "users": {},
    "templates": {},
    "notifications": {},
    "webhook_subscriptions": {},
    "events": [],
    "webhook_deliveries": [],
    "idempotency": {},
}

counters = {
    "usr": count(1),
    "tpl": count(1),
    "ntf": count(1),
    "wh": count(1),
    "evt": count(1),
    "dlv": count(1),
}


def create_id(prefix: str) -> str:
    return f"{prefix}_{next(counters[prefix]):03d}"


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def json_response(body, status=200, headers=None):
    response = make_response(jsonify(body), status)
    if headers:
        for key, value in headers.items():
            response.headers[key] = value
    return response


def empty_response(status=204):
    return ("", status)


def api_error(status: int, code: str, message: str, details=None):
    body = {
        "error": {
            "code": code,
            "message": message,
        }
    }
    if details is not None:
        body["error"]["details"] = details
    return json_response(body, status)


def get_json_body():
    body = request.get_json(silent=True)
    return body if isinstance(body, dict) else {}


def paginate(items):
    page = max(1, int(request.args.get("page", 1)))
    page_size = min(100, max(1, int(request.args.get("pageSize", 20))))
    start = (page - 1) * page_size
    return {
        "data": items[start : start + page_size],
        "pagination": {
            "page": page,
            "pageSize": page_size,
            "total": len(items),
        },
    }


def notification_links(notification):
    links = {
        "self": {"href": f"/notifications/{notification['id']}"},
        "recipient": {"href": f"/users/{notification['recipientId']}"},
        "webhookEvents": {"href": f"/notifications/{notification['id']}/events"},
    }
    if notification["status"] == "failed":
        links["retry"] = {
            "href": f"/notifications/{notification['id']}/retry",
            "method": "POST",
        }
    return links


def public_notification(notification):
    return {
        **notification,
        "_links": notification_links(notification),
    }


def public_webhook_subscription(subscription):
    return {
        **subscription,
        "_links": {
            "self": {"href": f"/webhook-subscriptions/{subscription['id']}"},
            "test": {
                "href": f"/webhook-subscriptions/{subscription['id']}/test",
                "method": "POST",
            },
        },
    }


def validate_webhook_url(value: str) -> bool:
    try:
        parsed = urlparse(value)
    except ValueError:
        return False

    is_local_http = parsed.scheme == "http" and parsed.hostname in {
        "localhost",
        "127.0.0.1",
    }
    return parsed.scheme == "https" or is_local_http


def render_template(template, variables=None):
    variables = variables or {}

    def replace(text):
        def repl(match):
            key = match.group(1)
            return str(variables.get(key, ""))

        return re.sub(r"\{\{(\w+)\}\}", repl, str(text or ""))

    return {
        "title": replace(template.get("subject") or template["name"]),
        "content": replace(template["body"]),
    }


def sign_webhook(secret: str, timestamp: str, raw_body: str) -> str:
    message = f"{timestamp}.{raw_body}".encode("utf-8")
    return hmac.new(secret.encode("utf-8"), message, hashlib.sha256).hexdigest()


def deliver_webhook(subscription, event, attempt=1):
    delivery_id = create_id("dlv")
    raw_body = json.dumps(event, separators=(",", ":"))
    timestamp = str(int(time.time()))
    signature = sign_webhook(subscription["secret"], timestamp, raw_body)

    delivery = {
        "id": delivery_id,
        "subscriptionId": subscription["id"],
        "eventId": event["id"],
        "eventType": event["type"],
        "attempt": attempt,
        "status": "pending",
        "createdAt": now(),
    }
    db["webhook_deliveries"].append(delivery)

    req = Request(
        subscription["url"],
        data=raw_body.encode("utf-8"),
        method="POST",
        headers={
            "Content-Type": "application/json",
            "X-Webhook-Event": event["type"],
            "X-Webhook-Delivery": delivery_id,
            "X-Webhook-Timestamp": timestamp,
            "X-Webhook-Signature": f"sha256={signature}",
        },
    )

    try:
        with urlopen(req, timeout=WEBHOOK_TIMEOUT_SECONDS) as response:
            status_code = response.status
            delivery["statusCode"] = status_code
            delivery["status"] = "succeeded" if 200 <= status_code < 300 else "failed"
    except HTTPError as exc:
        delivery["statusCode"] = exc.code
        delivery["status"] = "failed"
        if exc.code >= 500 and attempt < 3:
            schedule_webhook_retry(subscription, event, attempt + 1)
    except URLError as exc:
        delivery["status"] = "failed"
        delivery["error"] = str(exc.reason)
        if attempt < 3:
            schedule_webhook_retry(subscription, event, attempt + 1)
    finally:
        delivery["completedAt"] = now()


def schedule_webhook_retry(subscription, event, attempt):
    delays = {
        2: 1,
        3: 5,
    }
    timer = threading.Timer(delays.get(attempt, 5), deliver_webhook, [subscription, event, attempt])
    timer.daemon = True
    timer.start()


def dispatch_webhook_event(event):
    subscriptions = [
        item
        for item in db["webhook_subscriptions"].values()
        if item["status"] == "active" and event["type"] in item["events"]
    ]

    for subscription in subscriptions:
        thread = threading.Thread(target=deliver_webhook, args=(subscription, event, 1), daemon=True)
        thread.start()


def emit_event(event_type: str, data):
    event = {
        "id": create_id("evt"),
        "type": event_type,
        "occurredAt": now(),
        "data": data,
    }
    db["events"].append(event)
    dispatch_webhook_event(event)
    return event


def queue_notification_delivery(notification):
    def worker():
        notification["deliveryAttempts"] = notification.get("deliveryAttempts", 0) + 1
        is_demo_failure = bool(re.search(r"fail|error", f"{notification['title']} {notification['content']}", re.I))
        should_fail = is_demo_failure and notification["deliveryAttempts"] == 1
        notification["status"] = "failed" if should_fail else "sent"
        notification["sentAt"] = None if should_fail else now()
        notification["failedAt"] = now() if should_fail else None
        notification["failureReason"] = "Demo failure triggered on first delivery attempt." if should_fail else None

        emit_event(
            "notification.failed" if should_fail else "notification.sent",
            {
                "notificationId": notification["id"],
                "recipientId": notification["recipientId"],
                "channel": notification["channel"],
                "status": notification["status"],
            },
        )

    timer = threading.Timer(0.3, worker)
    timer.daemon = True
    timer.start()


def seed_data():
    user = {
        "id": "usr_001",
        "email": "user@example.com",
        "phone": "+84901234567",
        "deviceTokens": ["device_token_1"],
        "createdAt": now(),
    }
    db["users"][user["id"]] = user
    next(counters["usr"])

    template = {
        "id": "tpl_001",
        "name": "Welcome message",
        "channel": "email",
        "subject": "Welcome, {{name}}",
        "body": "Hello {{name}}, welcome to our notification system.",
        "createdAt": now(),
    }
    db["templates"][template["id"]] = template
    next(counters["tpl"])


@app.get("/health")
def health():
    return jsonify({"status": "ok", "time": now()})


@app.route("/users", methods=["GET", "POST"])
def users_collection():
    if request.method == "GET":
        return jsonify(paginate(list(db["users"].values())))

    body = get_json_body()
    if not body.get("email") and not body.get("phone") and not isinstance(body.get("deviceTokens"), list):
        return api_error(400, "VALIDATION_ERROR", "At least one contact field is required.")

    user = {
        "id": create_id("usr"),
        "email": body.get("email"),
        "phone": body.get("phone"),
        "deviceTokens": body.get("deviceTokens") if isinstance(body.get("deviceTokens"), list) else [],
        "createdAt": now(),
    }
    db["users"][user["id"]] = user
    return json_response(user, 201, {"Location": f"/users/{user['id']}"})


@app.route("/users/<user_id>", methods=["GET", "PATCH", "DELETE"])
def users_item(user_id):
    user = db["users"].get(user_id)
    if not user:
        return api_error(404, "NOT_FOUND", "User not found.")

    if request.method == "GET":
        return jsonify(user)

    if request.method == "PATCH":
        body = get_json_body()
        for field in ["email", "phone", "deviceTokens"]:
            if field in body:
                user[field] = body[field] if field != "deviceTokens" or isinstance(body[field], list) else []
        user["updatedAt"] = now()
        return jsonify(user)

    del db["users"][user_id]
    return empty_response()


@app.route("/notification-templates", methods=["GET", "POST"])
def templates_collection():
    if request.method == "GET":
        return jsonify(paginate(list(db["templates"].values())))

    body = get_json_body()
    if not body.get("name") or not body.get("channel") or not body.get("body"):
        return api_error(400, "VALIDATION_ERROR", "Fields name, channel and body are required.")

    template = {
        "id": create_id("tpl"),
        "name": body["name"],
        "channel": body["channel"],
        "subject": body.get("subject", body["name"]),
        "body": body["body"],
        "createdAt": now(),
    }
    db["templates"][template["id"]] = template
    return json_response(template, 201, {"Location": f"/notification-templates/{template['id']}"})


@app.route("/notification-templates/<template_id>", methods=["GET", "PATCH", "DELETE"])
def templates_item(template_id):
    template = db["templates"].get(template_id)
    if not template:
        return api_error(404, "NOT_FOUND", "Template not found.")

    if request.method == "GET":
        return jsonify(template)

    if request.method == "PATCH":
        body = get_json_body()
        for field in ["name", "channel", "subject", "body"]:
            if field in body:
                template[field] = body[field]
        template["updatedAt"] = now()
        return jsonify(template)

    del db["templates"][template_id]
    return empty_response()


@app.route("/notifications", methods=["GET", "POST"])
def notifications_collection():
    if request.method == "GET":
        items = list(db["notifications"].values())
        for field in ["recipientId", "status", "channel"]:
            value = request.args.get(field)
            if value:
                items = [item for item in items if str(item.get(field)) == value]

        from_date = request.args.get("from")
        to_date = request.args.get("to")
        if from_date:
            items = [item for item in items if item["createdAt"] >= from_date]
        if to_date:
            items = [item for item in items if item["createdAt"] <= to_date]

        return jsonify(paginate([public_notification(item) for item in items]))

    idempotency_key = request.headers.get("Idempotency-Key")
    if idempotency_key and idempotency_key in db["idempotency"]:
        notification_id = db["idempotency"][idempotency_key]
        return jsonify(public_notification(db["notifications"][notification_id]))

    body = get_json_body()
    if not body.get("recipientId"):
        return api_error(400, "VALIDATION_ERROR", "Field recipientId is required.")

    user = db["users"].get(body["recipientId"])
    if not user:
        return api_error(404, "NOT_FOUND", "Recipient user not found.")

    channel = body.get("channel")
    title = body.get("title")
    content = body.get("content")
    template_id = None

    if body.get("templateId"):
        template = db["templates"].get(body["templateId"])
        if not template:
            return api_error(404, "NOT_FOUND", "Template not found.")
        rendered = render_template(template, body.get("variables"))
        channel = template["channel"]
        title = rendered["title"]
        content = rendered["content"]
        template_id = template["id"]

    if not channel or not title or not content:
        return api_error(
            400,
            "VALIDATION_ERROR",
            "Fields channel, title and content are required unless templateId is used.",
        )

    notification = {
        "id": create_id("ntf"),
        "recipientId": user["id"],
        "templateId": template_id,
        "channel": channel,
        "title": title,
        "content": content,
        "status": "pending",
        "deliveryAttempts": 0,
        "createdAt": now(),
        "sentAt": None,
        "failedAt": None,
        "failureReason": None,
    }
    db["notifications"][notification["id"]] = notification
    if idempotency_key:
        db["idempotency"][idempotency_key] = notification["id"]

    emit_event(
        "notification.created",
        {
            "notificationId": notification["id"],
            "recipientId": notification["recipientId"],
            "channel": notification["channel"],
            "status": notification["status"],
        },
    )
    queue_notification_delivery(notification)

    return json_response(public_notification(notification), 202, {"Location": f"/notifications/{notification['id']}"})


@app.get("/notifications/<notification_id>")
def notifications_item(notification_id):
    notification = db["notifications"].get(notification_id)
    if not notification:
        return api_error(404, "NOT_FOUND", "Notification not found.")
    return jsonify(public_notification(notification))


@app.post("/notifications/<notification_id>/retry")
def notifications_retry(notification_id):
    notification = db["notifications"].get(notification_id)
    if not notification:
        return api_error(404, "NOT_FOUND", "Notification not found.")

    if notification["status"] != "failed":
        return api_error(409, "CONFLICT", "Only failed notifications can be retried.")

    notification["status"] = "pending"
    notification["failedAt"] = None
    notification["failureReason"] = None
    notification["updatedAt"] = now()

    emit_event(
        "notification.created",
        {
            "notificationId": notification["id"],
            "recipientId": notification["recipientId"],
            "channel": notification["channel"],
            "status": notification["status"],
        },
    )
    queue_notification_delivery(notification)
    return json_response(public_notification(notification), 202)


@app.get("/notifications/<notification_id>/events")
def notifications_events(notification_id):
    notification = db["notifications"].get(notification_id)
    if not notification:
        return api_error(404, "NOT_FOUND", "Notification not found.")

    events = [event for event in db["events"] if event["data"].get("notificationId") == notification_id]
    return jsonify(paginate(events))


@app.route("/webhook-subscriptions", methods=["GET", "POST"])
def webhook_subscriptions_collection():
    if request.method == "GET":
        items = [public_webhook_subscription(item) for item in db["webhook_subscriptions"].values()]
        return jsonify(paginate(items))

    body = get_json_body()
    if not body.get("url") or not validate_webhook_url(body["url"]):
        return api_error(400, "INVALID_WEBHOOK_URL", "Webhook URL must use HTTPS, or HTTP for localhost demo.")
    if not isinstance(body.get("events"), list) or not body["events"]:
        return api_error(400, "VALIDATION_ERROR", "Field events must be a non-empty array.")

    subscription = {
        "id": create_id("wh"),
        "url": body["url"],
        "events": body["events"],
        "status": body.get("status", "active"),
        "secret": f"whsec_{hashlib.sha256(str(time.time()).encode()).hexdigest()[:32]}",
        "createdAt": now(),
    }
    db["webhook_subscriptions"][subscription["id"]] = subscription
    return json_response(
        public_webhook_subscription(subscription),
        201,
        {"Location": f"/webhook-subscriptions/{subscription['id']}"},
    )


@app.route("/webhook-subscriptions/<subscription_id>", methods=["GET", "PATCH", "DELETE"])
def webhook_subscriptions_item(subscription_id):
    subscription = db["webhook_subscriptions"].get(subscription_id)
    if not subscription:
        return api_error(404, "NOT_FOUND", "Webhook subscription not found.")

    if request.method == "GET":
        return jsonify(public_webhook_subscription(subscription))

    if request.method == "PATCH":
        body = get_json_body()
        if "url" in body:
            if not validate_webhook_url(body["url"]):
                return api_error(400, "INVALID_WEBHOOK_URL", "Webhook URL must use HTTPS, or HTTP for localhost demo.")
            subscription["url"] = body["url"]
        if "events" in body:
            if not isinstance(body["events"], list) or not body["events"]:
                return api_error(400, "VALIDATION_ERROR", "Field events must be a non-empty array.")
            subscription["events"] = body["events"]
        if "status" in body:
            subscription["status"] = body["status"]
        subscription["updatedAt"] = now()
        return jsonify(public_webhook_subscription(subscription))

    del db["webhook_subscriptions"][subscription_id]
    return empty_response()


@app.post("/webhook-subscriptions/<subscription_id>/test")
def webhook_subscriptions_test(subscription_id):
    subscription = db["webhook_subscriptions"].get(subscription_id)
    if not subscription:
        return api_error(404, "NOT_FOUND", "Webhook subscription not found.")

    event = {
        "id": create_id("evt"),
        "type": "webhook.test",
        "occurredAt": now(),
        "data": {
            "subscriptionId": subscription["id"],
            "message": "Test webhook delivery",
        },
    }
    db["events"].append(event)
    thread = threading.Thread(target=deliver_webhook, args=(subscription, event, 1), daemon=True)
    thread.start()
    return json_response(event, 202)


@app.get("/events")
def events_collection():
    return jsonify(paginate(db["events"]))


@app.get("/webhook-deliveries")
def webhook_deliveries_collection():
    return jsonify(paginate(db["webhook_deliveries"]))


@app.errorhandler(404)
def not_found(_):
    return api_error(404, "NOT_FOUND", "Endpoint not found.")


@app.errorhandler(405)
def method_not_allowed(_):
    return api_error(405, "METHOD_NOT_ALLOWED", "Method is not allowed.")


seed_data()


if __name__ == "__main__":
    app.run(host=APP_HOST, port=APP_PORT, debug=True)
