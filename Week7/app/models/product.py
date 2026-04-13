from bson import ObjectId
from datetime import datetime


def product_serializer(product) -> dict:
    """Chuyển MongoDB document thành dict JSON-friendly"""
    return {
        "_id": str(product["_id"]),
        "name": product.get("name", ""),
        "description": product.get("description", ""),
        "price": product.get("price", 0),
        "stock": product.get("stock", 0),
        "createdAt": str(product.get("createdAt", "")),
        "updatedAt": str(product.get("updatedAt", "")),
    }
