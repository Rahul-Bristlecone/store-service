from flask_jwt_extended import jwt_required
from flask_smorest import Blueprint, abort
from flask.views import MethodView
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from store_service.src.store_service.extensions.db import db
from store_service.src.store_service.models.store_db import StoreModel
from store_service.src.store_service.schemas.store_schema import StoreSchema, UpdateStoreSchema

# created a blueprint "stores" with description and Dunder method (__name__)
# Dunder is usually used for operator overloading
blp = Blueprint("stores", __name__, description="Operations on stores")


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
        store = StoreModel.query.get_or_404(store_id)
        db.session.delete(store)
        db.session.commit()
        return {"message":f"store deleted with store id " + store_id}
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
    @blp.arguments(UpdateStoreSchema)  # Validation of request data (i.e. store_data) for updating a store
    @blp.response(200, StoreSchema)
    def put(self, store_id, store_data):
        store = StoreModel.query.get_or_404(store_id)
        if store:
            store.name = store_data["name"]
        else:
            store = StoreModel(store_id=store_id, **store_data)

        return store


@blp.route("/stores")
class StoreList(MethodView):
    @blp.response(200, StoreSchema(many=True))
    def get(self):
        return StoreModel.query.all()
        # store = StoreModel.query.get_or_404(store_id)


@blp.route("/create_store")  # This is the end-point for creating a store
class StoreCreate(MethodView):
    # This class is used to create a store, it is not used to update a store
    # It is used to create a store with the name of the store, which is unique for each store
    # The store_id is generated using uuid4() which is a unique universal id
    # The store_id is not passed in the request data, it is generated automatically by the database
    @jwt_required()  # This method requires a valid JWT token to access
    @blp.arguments(StoreSchema)  # Validation of request data for creating a store (Marshmallow)
    @blp.response(201, StoreSchema)  # Decorating the response
    def post(self, store_data):
        # check if the name already exists, this can also be done using Marshmallow
        store = StoreModel(**store_data)
        try:
            db.session.add(store)
            db.session.commit()
        except IntegrityError:
            abort(400, message="Store already exists")
        except SQLAlchemyError:
            abort(500, message="Store not available while creating")

        return store

        # store_id = uuid.uuid4().hex  # unique universal id is being generated
        # new_store = {**store_data, "store_id": store_id}
        # stores_data.stores[store_id] = new_store
        # return stores_data.stores, 201
