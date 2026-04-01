import json
import os
from flask import request
from flask.views import MethodView
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from store_service.src.store_service.utils.edifact_transformer import transform_edifact_to_json

from store_service.src.store_service.extensions.db import db
from store_service.src.store_service.extensions.redis_client import redis_client
from store_service.src.store_service.models.order_details_model import OrderModel
from store_service.src.store_service.models.store_db import StoreModel
from store_service.src.store_service.schemas.store_schema import OrderSchema, PlainOrderSchema

# Create blueprint for Orders
blp = Blueprint("orders", __name__, description="Operations on orders")

def create_order_from_payload(order_data):
    """
    Shared logic to create an order in the database.
    Validates JWT, checks Redis session, and persists the order.
    """
    user_id = int(get_jwt_identity())
    token = request.headers.get("Authorization").split()[1]

    cached_session = redis_client.get(f"session:{user_id}")
    if not cached_session:
        abort(401, message="Session expired or revoked")

    try:
        session_data = json.loads(cached_session)
        cached_token = session_data.get("token")
    except Exception:
        abort(401, message="Invalid session data")

    if cached_token != token:
        abort(401, message="Session expired or revoked")

    user_store_number = order_data.pop("user_store_number")
    store = StoreModel.query.filter_by(user_store_number=user_store_number, user_id=user_id).first()
    if not store:
        abort(400, message="Store number does not exist for this user")

    # Inject user_id from JWT
    order = OrderModel(user_id=user_id, store_id=store.store_id, **order_data)

    try:
        db.session.add(order)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        abort(400, message="Order already exists")
    except SQLAlchemyError:
        db.session.rollback()
        abort(500, message="Error inserting order into database")

    return order


# -------------------------------
# Endpoint: /order/<order_id>
# -------------------------------
@blp.route("/order/<int:order_id>")
class OrderResource(MethodView):
    @blp.response(200, OrderSchema)
    def get(self, order_id):
        order = OrderModel.query.get_or_404(order_id)
        return order


# -------------------------------
# Endpoint: /orders
# -------------------------------
@blp.route("/orders")
class OrderList(MethodView):
    @jwt_required()
    @blp.response(200, OrderSchema(many=True))
    def get(self):
        user_id = int(get_jwt_identity())
        return OrderModel.query.filter_by(user_id=user_id).all()


# -------------------------------
# Endpoint: /create_order
# -------------------------------
@blp.route("/create_order")
class OrderCreate(MethodView):
    @jwt_required()
    @blp.arguments(PlainOrderSchema)
    @blp.response(201, OrderSchema)
    def post(self, order_data):
        return create_order_from_payload(order_data)

    
@blp.route("/upload_edi")
class UploadEdiResource(MethodView):
    @jwt_required()
    @blp.response(201, OrderSchema)
    def post(self):
        if "file" not in request.files:
            abort(400, message="No file uploaded")

        edi_file = request.files["file"]
        file_path = os.path.join("/tmp", edi_file.filename)
        edi_file.save(file_path)

        # Transform EDIFACT → JSON
        order_data = transform_edifact_to_json(file_path)

        # Reuse the same order creation logic
        return create_order_from_payload(order_data)