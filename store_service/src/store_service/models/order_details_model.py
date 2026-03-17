from store_service.src.store_service.extensions.db import db
from datetime import datetime, UTC

# docker exec -it user-service bash
# python -m alembic revision --autogenerate -m "Added new column"
# python -m alembic upgrade head

class OrderModel(db.Model):
    __tablename__ = "orders"

    order_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, nullable=False)   # just user ID
    store_id = db.Column(db.Integer, db.ForeignKey("stores.store_id"), nullable=False)  # just store ID

    order_status = db.Column(
        db.Enum("pending", "processing", "shipped", "delivered", "cancelled", name="order_status_enum"),
        default="pending",
        nullable=False
    )

    total_amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(10), default="INR", nullable=False)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC), nullable=False)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC), nullable=False)

    items = db.relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    store = db.relationship("StoreModel", back_populates="orders")