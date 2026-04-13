from flask import Flask
from flask_pymongo import PyMongo
from dotenv import load_dotenv
import os

load_dotenv()

mongo = PyMongo()


def create_app():
    app = Flask(__name__)
    app.config["MONGO_URI"] = os.getenv("MONGODB_URI")

    mongo.init_app(app)

    from app.routes.product_routes import product_bp
    app.register_blueprint(product_bp, url_prefix="/api/products")

    @app.route("/")
    def index():
        return {"message": "Product API đang chạy!"}

    return app
