from store_service.src.store_service.extensions.db import db
from store_service.src.store_service.models.item_tags_db import ItemTags


class TagsModel(db.Model):  # Mapping the class to the rows of the table
    __tablename__ = "tags"  # Telling the name of the table i.e. tags to SqlAlchemy

    tag_id = db.Column(db.Integer, primary_key=True)  # need not be passed
    name = db.Column(db.String(40), unique=True, nullable=False)
    # category = db.Column(db.String(40), unique=True, nullable=False)  # unique to Range->category
    store_id = db.Column(db.Integer, db.ForeignKey("stores.store_id"), unique=False, nullable=False)
    stores = db.relationship("StoreModel", back_populates="tags")
    # SQLAlchemy will go through item_tags_db to find out what items, this tag is related to ItemTags table will have
    # a foreign key column 'tag_id' which is linked to primary key column 'tag_id' of tag table
    items = db.relationship("ItemModel", back_populates="tags", secondary=ItemTags)
