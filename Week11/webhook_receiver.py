from flask import Flask, jsonify, request


app = Flask(__name__)


@app.post("/webhooks/notifications")
def receive_webhook():
    print("Webhook received")
    print("Event:", request.headers.get("X-Webhook-Event"))
    print("Delivery:", request.headers.get("X-Webhook-Delivery"))
    print("Timestamp:", request.headers.get("X-Webhook-Timestamp"))
    print("Signature:", request.headers.get("X-Webhook-Signature"))
    print("Body:", request.get_data(as_text=True))
    print("")
    return jsonify({"received": True})


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=4000, debug=True)
