from store_service.src.store_service.extensions.db import db

class StoreModel(db.Model):
    __tablename__ = "stores"

    store_id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, nullable=False)  # new field
    store_name = db.Column(db.String(40), unique=True, nullable=False)

    # Address fields
    address_line1 = db.Column(db.String(100), nullable=False)
    address_line2 = db.Column(db.String(100), nullable=True)
    address_line3 = db.Column(db.String(100), nullable=True)
    pin_code = db.Column(db.String(10), nullable=False)
    state_code = db.Column(db.String(10), nullable=False)
    country_code = db.Column(db.String(10), nullable=False)

    shipping_time = db.Column(db.Integer, nullable=False)  # e.g., days to ship

    # Relationships
    items = db.relationship("ItemModel", back_populates="store", cascade="all, delete")
    tags = db.relationship("TagsModel", back_populates="store")
    orders = db.relationship("OrderModel", back_populates="store")

