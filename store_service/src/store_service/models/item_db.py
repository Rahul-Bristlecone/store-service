from store_service.src.store_service.extensions.db import db
from store_service.src.store_service.models.item_tags_db import ItemTags


class ItemModel(db.Model):  # Mapping the class to the rows of the table
    __tablename__ = "items"  # Telling the name of the table i.e., items to SqlAlchemy

    product_id = db.Column(db.Integer, primary_key=True)  # need not be passed
    name = db.Column(db.String(40), unique=True, nullable=False)
    # category = db.Column(db.String(40), unique=True, nullable=False)  # unique to Range->category
    price = db.Column(db.Float, unique=False, nullable=False)  # foreign key
    store_id = db.Column(db.Integer, db.ForeignKey("stores.store_id"), unique=False, nullable=False)

    stores = db.relationship("StoreModel", back_populates="items")
    tags = db.relationship("TagsModel", back_populates="items", secondary=ItemTags)
