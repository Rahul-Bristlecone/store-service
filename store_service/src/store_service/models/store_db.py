from store_service.src.store_service.extensions.db import db


class StoreModel(db.Model):  # Mapping the class to the rows of the table
    __tablename__ = "stores"  # Telling the name of the table i.e., stores to SqlAlchemy

    store_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40), unique=True, nullable=False)
    #  cascade is used if store is parent is deleted, then children are automatically deleted.
    items = db.relationship("ItemModel", back_populates="stores", cascade="all, delete")
    tags = db.relationship("TagsModel", back_populates="stores")