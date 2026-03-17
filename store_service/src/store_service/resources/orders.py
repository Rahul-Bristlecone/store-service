import json
from flask import request
from flask.views import MethodView
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from store_service.src.store_service.extensions.db import db
from store_service.src.store_service.extensions.redis_client import redis_client
from store_service.src.store_service.models.order_details_model import OrderModel
from store_service.src.store_service.models.order_item import OrderItem
from store_service.src.store_service.schemas.store_schema import OrderSchema, PlainOrderSchema

# Create blueprint for Orders
blp = Blueprint("orders", __name__, description="Operations on orders")

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
    @blp.response(200, OrderSchema(many=True))
    def get(self):
        return OrderModel.query.all()

# -------------------------------
# Endpoint: /create_order
# -------------------------------
@blp.route("/create_order")
class OrderCreate(MethodView):
    @jwt_required()
    @blp.arguments(PlainOrderSchema)   # validate incoming request
    @blp.response(201, OrderSchema)    # return created order
    def post(self, order_data):
        user_id = get_jwt_identity()
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

        # Inject user_id from JWT
        order = OrderModel(user_id=user_id, **order_data)

        try:
            db.session.add(order)
            db.session.commit()
        except IntegrityError:
            abort(400, message="Order already exists")
        except SQLAlchemyError:
            abort(500, message="Error inserting order into database")
    
        return order