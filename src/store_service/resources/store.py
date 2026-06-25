import json

from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_smorest import Blueprint, abort
from flask.views import MethodView
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from store_service.extensions.redis_client import redis_client
from store_service.extensions.db import db
from store_service.models.store_db import StoreModel
from store_service.schemas.store_schema import StoreSchema

# created a blueprint "stores" with description and Dunder method (__name__)
# Dunder is usually used for operator overloading
blp = Blueprint("stores", __name__, description="Operations on stores")

def validate_active_session(user_id):
    auth_header = request.headers.get("Authorization", "")
    token_parts = auth_header.split()
    if len(token_parts) != 2:
        abort(401, message="Missing or invalid authorization token")

    token = token_parts[1]
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

def get_user_product_or_404(store_id, user_id):
    store = StoreModel.query.filter_by(store_id=store_id, user_id=user_id).first()
    if not store:
        abort(404, message="Store not found")
    return store

# Inherit a class from MethodView whose methods will route to specific end-points because the blue-print is--
# --prepared for that particular class
# This blueprint method will route all the methods of this class to this particular end-point
@blp.route("/store/<string:store_id>")
class Store(MethodView):
    @blp.response(200, StoreSchema)
    def get(self, store_id):
        store = StoreModel.query.get_or_404(store_id)
        return store

    # except KeyError:
    #     # return {"message": "store not found"}, 404
    #     abort(404, message="store not found")
    @jwt_required()  # This method requires a valid JWT token to access
    # @blp.response(200, StoreSchema)
    def delete(self, store_id):
        user_id = int(get_jwt_identity())
        validate_active_session(user_id)
        store = get_user_product_or_404(store_id, user_id)
        db.session.delete(store)
        db.session.commit()
        return {"message": "store deleted with store id " + store_id}
        # raise NotImplementedError("Not implemented delete store")
        # try:
        #     store = StoreModel.query.get_or_404(store_id)
        #     db.db.session.delete(store)
        #     db.db.session.commit()
        #     return {"message": "store deleted"}
        # except KeyError:
        #     # return {"message": "store not found"}, 404
        #     abort(404, message="store not found")

    # TODO if incoming data for a store has some blank values apart from the name of the store, not to be updated
    @jwt_required()  # This method requires a valid JWT token to access
    @blp.arguments(StoreSchema)  # Validation of request data (i.e. store_data) for updating a store
    @blp.response(200, StoreSchema)
    def put(self, store_data, store_id):
        user_id = int(get_jwt_identity())
        validate_active_session(user_id)

        store = get_user_product_or_404(store_id, user_id)

        if "product_code" in store_data:
            abort(400, message="product_code cannot be updated")

        # Ensure product ownership cannot be reassigned via request payload.
        store_data.pop("user_id", None)
        store_data.pop("store_id", None)

        for key, value in store_data.items():
            setattr(store, key, value)

        try:
            db.session.add(store)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            abort(400, message="Product code or barcode already exists")
        except SQLAlchemyError:
            db.session.rollback()
            abort(500, message="Error updating product in database")

        return store


@blp.route("/stores")
class StoreList(MethodView):
    @jwt_required()  # remove this later
    @blp.response(200, StoreSchema(many=True))
    def get(self):
        # return StoreModel.query.all() - uncomment
        # store = StoreModel.query.get_or_404(store_id)

        # remove this part later
        user_id = int(get_jwt_identity())
        return StoreModel.query.filter_by(user_id=user_id).all()


@blp.route("/create_store")  # This is the end-point for creating a store
class StoreCreate(MethodView):
    # MethodView is a class that provides methods for handling HTTP requests (GET, POST, PUT, DELETE, etc.) in a class-based view.
    # This class is used to create a store, it is not used to update a store
    # It is used to create a store with the name of the store, which is unique for each store
    # The store_id is generated using uuid4() which is a unique universal id
    # The store_id is not passed in the request data, it is generated automatically by the database
    @jwt_required()  # This method requires a valid JWT token to access
    @blp.arguments(StoreSchema)  # Validation of request data for creating a store (Marshmallow)
    @blp.response(201, StoreSchema)  # Decorating the response
    def post(self, store_data):
        user_id = int(get_jwt_identity())
        validate_active_session(user_id)

        try:
            insert_statement = text(
                """
                INSERT INTO stores (
                    store_number,
                    customer_name,
                    store_name,
                    address_line1,
                    address_line2,
                    address_line3,
                    pin_code,
                    state_code,
                    country_code,
                    shipping_time,
                    user_id
                ) VALUES (
                    :store_number,
                    :customer_name,
                    :store_name,
                    :address_line1,
                    :address_line2,
                    :address_line3,
                    :pin_code,
                    :state_code,
                    :country_code,
                    :shipping_time,
                    :user_id
                )
                """
            )
            db.session.execute(insert_statement, {**store_data, "user_id": user_id})
            db.session.commit()

            store = StoreModel.query.filter_by(
                user_id=user_id,
                store_number=store_data["store_number"],
            ).first()
        except IntegrityError:
            db.session.rollback()
            abort(400, message="Store number already exists for this user")
        except SQLAlchemyError as e:
            db.session.rollback()
            print("SQLAlchemy error:", str(e))
            abort(500, message="Store not available while creating")

        return store

        # store_id = uuid.uuid4().hex  # unique universal id is being generated
        # new_store = {**store_data, "store_id": store_id}
        # stores_data.stores[store_id] = new_store
        # return stores_data.stores, 201
