from flask import request, jsonify
from flask_pymongo import PyMongo
from bson import ObjectId
from bson.errors import InvalidId
from datetime import datetime
from app import mongo

# GET /api/products


def get_all_products():
    products = mongo.db.products.find()
    return jsonify([product_serializer(p) for p in products]), 200

# GET /api/products/<id>


def get_product_by_id(id):
    try:
        product = mongo.db.products.find_one({"_id": ObjectId(id)})
        if not product:
            return jsonify({"message": "Không tìm thấy sản phẩm"}), 404
        return jsonify(product_serializer(product)), 200
    except InvalidId:
        return jsonify({"message": "ID không hợp lệ"}), 400

# POST /api/products


def create_product():
    data = request.get_json()
    if not data.get("name") or not data.get("price"):
        return jsonify({"message": "Thiếu name hoặc price"}), 400

    new_product = {
        "name": data["name"],
        "description": data.get("description", ""),
        "price": data["price"],
        "stock": data.get("stock", 0),
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow(),
    }
    result = mongo.db.products.insert_one(new_product)
    new_product["_id"] = result.inserted_id
    return jsonify(product_serializer(new_product)), 201

# PUT /api/products/<id>


def update_product(id):
    try:
        data = request.get_json()
        updated_fields = {
            "name": data.get("name"),
            "description": data.get("description"),
            "price": data.get("price"),
            "stock": data.get("stock"),
            "updatedAt": datetime.utcnow(),
        }
        # Bỏ những field None
        updated_fields = {k: v for k,
                          v in updated_fields.items() if v is not None}

        result = mongo.db.products.find_one_and_update(
            {"_id": ObjectId(id)},
            {"$set": updated_fields},
            return_document=True
        )
        if not result:
            return jsonify({"message": "Không tìm thấy sản phẩm"}), 404
        return jsonify(product_serializer(result)), 200
    except InvalidId:
        return jsonify({"message": "ID không hợp lệ"}), 400

# DELETE /api/products/<id>


def delete_product(id):
    try:
        result = mongo.db.products.find_one_and_delete({"_id": ObjectId(id)})
        if not result:
            return jsonify({"message": "Không tìm thấy sản phẩm"}), 404
        return jsonify({"message": "Xóa thành công"}), 200
    except InvalidId:
        return jsonify({"message": "ID không hợp lệ"}), 400


def product_serializer(product) -> dict:
    return {
        "_id": str(product["_id"]),
        "name": product.get("name", ""),
        "description": product.get("description", ""),
        "price": product.get("price", 0),
        "stock": product.get("stock", 0),
        "createdAt": str(product.get("createdAt", "")),
        "updatedAt": str(product.get("updatedAt", "")),
    }
