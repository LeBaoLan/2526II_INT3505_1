"""
Demo: Logging (Loguru) + Monitoring (Prometheus) + Rate Limiting (Flask-Limiter)
"""
import time
import random
import sys
import os
from flask import Flask, jsonify, request
from loguru import logger
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# ─── Loguru ────────────────────────────────────────────────────────
logger.remove()
logger.add(sys.stdout,
           format="<green>{time:HH:mm:ss}</green> | <level>{level:<8}</level> | <level>{message}</level>",
           colorize=True, level="DEBUG")
os.makedirs("logs", exist_ok=True)
logger.add("logs/app.log",    rotation="10 MB",
           retention="7 days",  level="INFO")
logger.add("logs/errors.log", rotation="5 MB",
           retention="30 days", level="ERROR")

# ─── Prometheus metrics ────────────────────────────────────────────
REQUEST_COUNT = Counter("http_requests_total",
                        "Tổng HTTP requests",     ["method", "endpoint", "status"])
REQUEST_LATENCY = Histogram("http_request_duration_seconds",  "Latency (giây)",         ["endpoint"],
                            buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.0])
ACTIVE_REQUESTS = Gauge("http_active_requests",
                        "Requests đang xử lý")
ERROR_COUNT = Counter("app_errors_total",
                      "Tổng lỗi ứng dụng",     ["type"])
RATE_LIMIT_HIT = Counter("http_rate_limit_exceeded_total",
                         "Số lần bị rate limit",  ["endpoint"])

# ─── Flask + Limiter ───────────────────────────────────────────────
app = Flask(__name__)

limiter = Limiter(
    key_func=get_remote_address,       # phân biệt theo IP client
    app=app,
    default_limits=["60 per minute"],  # giới hạn mặc định toàn app
    storage_uri="memory://",           # lưu state in-memory (1 process)
)


@app.errorhandler(429)
def rate_limit_handler(e):
    RATE_LIMIT_HIT.labels(endpoint=request.path).inc()
    logger.warning(
        f"RATE LIMIT: {request.method} {request.path} | IP: {request.remote_addr} | {e.description}")
    return jsonify({
        "error":   "Too Many Requests",
        "message": "Bạn gửi request quá nhanh. Vui lòng chờ và thử lại.",
        "limit":   str(e.description),
    }), 429

# ─── Middleware đo lường ───────────────────────────────────────────


@app.before_request
def before_request():
    request.start_time = time.time()
    ACTIVE_REQUESTS.inc()


@app.after_request
def after_request(response):
    duration = time.time() - request.start_time
    ACTIVE_REQUESTS.dec()
    if request.path != "/metrics":
        REQUEST_COUNT.labels(
            method=request.method, endpoint=request.path, status=response.status_code).inc()
        REQUEST_LATENCY.labels(endpoint=request.path).observe(duration)
        msg = f"{request.method} {request.path} -> {response.status_code} ({duration*1000:.1f}ms)"
        if response.status_code == 429:
            pass
        elif response.status_code >= 500:
            logger.error(msg)
        elif response.status_code >= 400:
            logger.warning(msg)
        else:
            logger.info(msg)
    return response

# ─── Endpoints ─────────────────────────────────────────────────────


@app.route("/")
def index():
    return jsonify({
        "service": "Demo Logging + Monitoring + Rate Limiting",
        "rate_limits": {
            "/users":    "5 req/phút",
            "/products": "10 req/phút",
            "/slow":     "3 req/phút",
            "/error":    "60 req/phút (mặc định)",
            "/health":   "không giới hạn",
        },
    })


@app.route("/health")
@limiter.exempt
def health():
    return jsonify({"status": "healthy", "timestamp": time.time()})


@app.route("/users")
@limiter.limit("5 per minute")    # chặt: chỉ 5 lần/phút
def get_users():
    time.sleep(random.uniform(0.01, 0.1))
    return jsonify([
        {"id": 1, "name": "Nguyen Van An"},
        {"id": 2, "name": "Tran Thi Binh"},
    ])


@app.route("/products")
@limiter.limit("10 per minute")   # 10 lần/phút
def get_products():
    time.sleep(random.uniform(0.05, 0.2))
    return jsonify([{"id": 1, "name": "Laptop Dell", "price": 15000000}])


@app.route("/slow")
@limiter.limit("3 per minute")    # rất chặt vì tốn tài nguyên
def slow_endpoint():
    delay = random.uniform(0.5, 1.5)
    time.sleep(delay)
    logger.warning(f"Endpoint cham! Mat {delay:.2f}s")
    return jsonify({"message": "Xong roi, nhung cham lam..."})


@app.route("/error")
def trigger_error():
    err = random.choice(["DatabaseError", "TimeoutError", "ValidationError"])
    ERROR_COUNT.labels(type=err).inc()
    logger.error(f"Loi xay ra: {err}")
    return jsonify({"error": err}), 500


@app.route("/metrics")
@limiter.exempt
def metrics():
    return generate_latest(), 200, {"Content-Type": CONTENT_TYPE_LATEST}


if __name__ == "__main__":
    logger.success("Server khoi dong tai http://localhost:5000")
    logger.info(
        "Rate limits: /users=5/phut | /products=10/phut | /slow=3/phut | default=60/phut")
    app.run(debug=False, port=5000)
