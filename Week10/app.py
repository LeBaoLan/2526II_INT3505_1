import time
import random
from flask import Flask, jsonify, request
from loguru import logger
from prometheus_client import (
    Counter, Histogram, Gauge,
    generate_latest, CONTENT_TYPE_LATEST
)
import sys, os

logger.remove()
logger.add(sys.stdout, format="{time:YYYY-MM-DD HH:mm:ss} | {level:<8} | {message}", colorize=True)
os.makedirs("logs", exist_ok=True)
logger.add("logs/app.log", rotation="1 MB", retention="7 days", level="DEBUG",
           format="{time:YYYY-MM-DD HH:mm:ss} | {level:<8} | {name}:{line} | {message}")

REQUEST_COUNT = Counter("http_requests_total", "Total HTTP requests", ["method", "endpoint", "status"])
REQUEST_LATENCY = Histogram("http_request_duration_seconds", "HTTP request latency", ["endpoint"],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.0])
ACTIVE_REQUESTS = Gauge("http_active_requests", "Number of active requests")
ERROR_COUNT = Counter("app_errors_total", "Total application errors", ["type"])

app = Flask(__name__)

@app.before_request
def before_request():
    request.start_time = time.time()
    ACTIVE_REQUESTS.inc()
    logger.debug(f"→ {request.method} {request.path}")

@app.after_request
def after_request(response):
    duration = time.time() - request.start_time
    ACTIVE_REQUESTS.dec()
    if request.path != "/metrics":
        REQUEST_COUNT.labels(method=request.method, endpoint=request.path, status=response.status_code).inc()
        REQUEST_LATENCY.labels(endpoint=request.path).observe(duration)
        level = "info" if response.status_code < 400 else "warning"
        getattr(logger, level)(f"{request.method} {request.path} → {response.status_code} ({duration*1000:.1f}ms)")
    return response

@app.route("/")
def index():
    return jsonify({"message": "Hello! API đang chạy", "status": "ok"})

@app.route("/users")
def get_users():
    time.sleep(random.uniform(0.01, 0.1))
    users = [{"id": 1, "name": "Nguyen Van An"}, {"id": 2, "name": "Tran Thi Binh"}]
    logger.info(f"Tra ve {len(users)} users")
    return jsonify(users)

@app.route("/products")
def get_products():
    time.sleep(random.uniform(0.05, 0.3))
    return jsonify([{"id": 1, "name": "Laptop Dell", "price": 15000000}])

@app.route("/slow")
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
def metrics():
    return generate_latest(), 200, {"Content-Type": CONTENT_TYPE_LATEST}

@app.route("/health")
def health():
    return jsonify({"status": "healthy"})

if __name__ == "__main__":
    logger.info("Server khoi dong tai http://localhost:5000")
    logger.info("Prometheus metrics tai http://localhost:5000/metrics")
    app.run(debug=False, port=5000)
