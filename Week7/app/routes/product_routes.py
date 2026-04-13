from flask import Blueprint
from app.controllers.product_controller import (
    get_all_products,
    get_product_by_id,
    create_product,
    update_product,
    delete_product,
)

product_bp = Blueprint("products", __name__)

product_bp.route("/", methods=["GET"])(get_all_products)
product_bp.route("/", methods=["POST"])(create_product)
product_bp.route("/<id>", methods=["GET"])(get_product_by_id)
product_bp.route("/<id>", methods=["PUT"])(update_product)
product_bp.route("/<id>", methods=["DELETE"])(delete_product)
