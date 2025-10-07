from flask.views import MethodView
from flask_jwt_extended import jwt_required
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError

from store_service.src.store_service.extensions.db import db
from store_service.src.store_service.models.item_db import ItemModel
from store_service.src.store_service.schemas.store_schema import ItemSchema, UpdateItemSchema

# created a blueprint "stores" with description and Dunder method (__name__)
# Dunder is usually used for operator overloading
blp = Blueprint("Items", __name__, description="Operations on Items")

# create a class from MethodView whose methods will route to specific end-points because the blue-print is--
# --prepared for that particular class
# This blueprint method will route all the methods of this class to this particular end-point
@blp.route("/item/<string:item_id>")
class Item(MethodView):
    @blp.response(200, ItemSchema)
    def get(self, item_id):
        try:
            item = ItemModel.query.get_or_404(item_id)
            return item
        except KeyError:
            # return {"message": "store not found"}, 404
            abort(404, message="item not found")

    @jwt_required()  # This method requires a valid JWT token to access
    # JWT token is required for end-points which can't be access unless user is logged in
    # @blp.response(200, ItemSchema)
    def delete(self, item_id):
        item = ItemModel.query.get_or_404(item_id)
        db.session.delete(item)
        db.session.commit()
        return {"message": "Item deleted with item id " + item_id}

        # try:
        #     item = ItemModel.query.get_or_404(item_id)
        #     db.db.session.delete(item)
        #     db.db.session.commit()
        #     return {"message": "item deleted"}
        # except KeyError:
        #     # return {"message": "store not found"}, 404
        #     abort(404, message="item not found")
    @jwt_required()  # This method requires a valid JWT token to access
    # JWT token is required for end-points which can't be access unless user is logged in
    @blp.arguments(UpdateItemSchema)
    @blp.response(200, ItemSchema)
    def put(self, item_data, item_id):
        item = ItemModel.query.get(item_id)
        if item:
            item.price = item_data["price"]
            item.name = item_data["name"]
        else:
            item = ItemModel(product_id=item_id, **item_data)

        db.session.add(item)
        db.session.commit()

        return item


@blp.route("/items")
class ItemList(MethodView):
    @blp.response(200, ItemSchema(many=True))
    def get(self):
        return ItemModel.query.all()
        # store = StoreModel.query.get_or_404(store_id)

    # TODO if incoming data for a store has some blank values apart from the name of the store, not to be updated
    # @blp.arguments(UpdateStoreSchema)  # Validation of request data (i.e. store_data) for updating a store
    # def put(self, store_data, store_id):
    #     # request_data = request.get_json()
    #     try:
    #         store = StoreModel.query.get_or_404(store_id)
    #         store |= store_data
    #         db.db.session.commit()
    #         return store
    #     except KeyError:
    #         abort(400, message="Store not available")

    @jwt_required()
    # JWT token is required for end-points which can't be access unless user is logged in
    @blp.arguments(ItemSchema)  # Validation of request data for creating a store (Marshmallow)
    @blp.response(201, ItemSchema)  # Decorating the response
    def post(self, item_data):
        # check if the name already exists, this can also be done using Marshmallow
        item = ItemModel(**item_data)
        try:
            db.session.add(item)
            db.session.commit()

        except SQLAlchemyError:
            abort(500, message="Store not available while Inserting item")

        return item

        # store_id = uuid.uuid4().hex  # unique universal id is being generated
        # new_store = {**store_data, "store_id": store_id}
        # stores_data.stores[store_id] = new_store
        # return stores_data.stores, 201
