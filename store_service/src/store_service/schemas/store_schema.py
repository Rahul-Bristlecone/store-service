from marshmallow import Schema, fields

# TODO Nested data validations using Marshmallow
# TODO Duplicate data validations

# This is for validation of incoming request data
class PlainItemSchema(Schema):
    # store_id = fields.Str(dump_only=True) # commented because dealt in another class below
    product_id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    price = fields.Float(required=True)


class PlainStoreSchema(Schema):
    store_id = fields.Int(dump_only=True)
    user_store_number = fields.Int(required=True)
    store_name = fields.Str(required=True)

    customer_id = fields.Int(required=True)
    user_id = fields.Int(dump_only=True)  # comment later
    address_line1 = fields.Str(required=True)
    address_line2 = fields.Str()
    address_line3 = fields.Str()
    pin_code = fields.Str(required=True)
    state_code = fields.Str(required=True)
    country_code = fields.Str(required=True)
    shipping_time = fields.Int(required=True)


# Plain schema for orders (basic fields)
class PlainOrderSchema(Schema):
    order_id = fields.Int(dump_only=True)
    store_id = fields.Int(dump_only=True)
    user_store_number = fields.Int(required=True, load_only=True)

    user_id = fields.Int(dump_only=True)

    order_status = fields.Str(required=True)
    total_amount = fields.Float(required=True)
    currency = fields.Str(required=True)

    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class PlainTagsSchema(Schema):
    tag_id = fields.Int(dump_only=True)
    name = fields.Str(required=True)


class UpdateStoreSchema(Schema):
    store_id = fields.Str(required=True)
    name = fields.Str(required=True)
    product = fields.List(fields.Str())


class UpdateItemSchema(Schema):
    name = fields.Str()
    price = fields.Int()
    store_id = fields.Int()


class ItemSchema(PlainItemSchema):
    store_id = fields.Int(required=True, load_only=True)  # store_id will automatically load up when use ItemSchema
    stores = fields.Nested(PlainStoreSchema(), dump_only=True)
    # Multiple tags can be associated with one item. Hence, Nested List
    tags = fields.List(fields.Nested(PlainTagsSchema()), dump_only=True)


# Extended schema for orders with nested relationships
class OrderSchema(PlainOrderSchema):
    # Just include IDs here
    user_id = fields.Int(dump_only=True)
    store_id = fields.Int(dump_only=True)

    # Nested items still make sense because they belong to orders
    items = fields.List(fields.Nested(PlainOrderSchema()), dump_only=True)


class StoreSchema(PlainStoreSchema):
    items = fields.List(fields.Nested(PlainItemSchema()), dump_only=True)
    tags = fields.List(fields.Nested(PlainTagsSchema(), dump_only=True))


class TagsSchema(PlainTagsSchema):
    store_id = fields.Int(load_only=True)  # store_id will automatically load up when use ItemSchema
    store = fields.Nested(PlainStoreSchema(), dump_only=True)
    # Multiple items can be associated with one tag. Hence, Nested List
    items = fields.List(fields.Nested(PlainItemSchema(), dump_only=True))


# Schema to return information about item and tag that are related
class TagAndItemSchema(Schema):
    message = fields.Str()
    item = fields.Nested(ItemSchema())
    tag = fields.Nested(TagsSchema())