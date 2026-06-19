from marshmallow import Schema, fields

# TODO Nested data validations using Marshmallow
# TODO Duplicate data validations

# This is for validation of incoming request data

class StoreSchema(Schema):
    store_id = fields.Int(dump_only=True)
    user_id = fields.Int(dump_only=True)

    store_number = fields.Int(allow_none=False)
    store_name = fields.Str(allow_none=False)
    customer_name = fields.Str(required=True, allow_none=False)
    
    address_line1 = fields.Str()
    address_line2 = fields.Str(allow_none=True)
    address_line3 = fields.Str(allow_none=True)
    pin_code = fields.Str()
    state_code = fields.Str()
    country_code = fields.Str()
    shipping_time = fields.Int()