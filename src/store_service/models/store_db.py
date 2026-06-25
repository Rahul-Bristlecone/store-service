from store_service.extensions.db import db

class StoreModel(db.Model):
    __tablename__ = "stores"
    __table_args__ = (
        db.UniqueConstraint("user_id", "store_number", name="uq_stores_user_id_store_number"),
    )

    store_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    store_number = db.Column(db.Integer, nullable=False)
    customer_name = db.Column(db.String(100), nullable=False)
    store_name = db.Column(db.String(40), nullable=False)

    user_id = db.Column(db.Integer, nullable=False)

    # Address fields
    address_line1 = db.Column(db.String(100), nullable=False)
    address_line2 = db.Column(db.String(100), nullable=True)
    address_line3 = db.Column(db.String(100), nullable=True)
    pin_code = db.Column(db.String(10), nullable=False)
    state_code = db.Column(db.String(10), nullable=False)
    country_code = db.Column(db.String(10), nullable=False)

    shipping_time = db.Column(db.Integer, nullable=False)  # e.g., days to ship