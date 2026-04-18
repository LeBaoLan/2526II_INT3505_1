from flask import Flask, jsonify, request

app = Flask(__name__)

todos = [
    {"id": 1, "title": "Learn API Testing", "done": False},
    {"id": 2, "title": "Use Postman", "done": True},
]
next_id = 3

# GET /todos - Lấy tất cả


@app.route("/todos", methods=["GET"])
def get_todos():
    return jsonify(todos)

# GET /todos/<id> - Lấy 1 todo


@app.route("/todos/<int:id>", methods=["GET"])
def get_todo(id):
    todo = next((t for t in todos if t["id"] == id), None)
    if not todo:
        return jsonify({"error": "Not found"}), 404
    return jsonify(todo)

# POST /todos - Tạo mới


@app.route("/todos", methods=["POST"])
def create_todo():
    global next_id
    data = request.get_json()
    if not data or "title" not in data:
        return jsonify({"error": "title is required"}), 400
    todo = {"id": next_id, "title": data["title"], "done": False}
    next_id += 1
    todos.append(todo)
    return jsonify(todo), 201

# PUT /todos/<id> - Cập nhật


@app.route("/todos/<int:id>", methods=["PUT"])
def update_todo(id):
    todo = next((t for t in todos if t["id"] == id), None)
    if not todo:
        return jsonify({"error": "Not found"}), 404
    data = request.get_json()
    if "title" in data:
        todo["title"] = data["title"]
    if "done" in data:
        todo["done"] = data["done"]
    return jsonify(todo)

# DELETE /todos/<id> - Xóa


@app.route("/todos/<int:id>", methods=["DELETE"])
def delete_todo(id):
    global todos
    todo = next((t for t in todos if t["id"] == id), None)
    if not todo:
        return jsonify({"error": "Not found"}), 404
    todos = [t for t in todos if t["id"] != id]
    return "", 204


if __name__ == "__main__":
    app.run(debug=True, port=3000)
