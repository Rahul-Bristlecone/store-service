from store_service.src.store_service.extensions.db import db

# ItemTags table is a secondary table created from tags table and Items table.
# relationship - we have tags for a store, and those tags will now be associated with items.
# one item can have multiple tags (moisturizer and gender) and that tag can be associated with --
# -- multiple items, all these tags and items are part of a store

# class ItemTagsModel(db.Model):  # Mapping the class to the rows of the table
#     __tablename__ = "ItemTags"
#
#     id = db.Column(db.Integer, primary_key=True)
#     itemid = db.Column(db.Integer, db.ForeignKey("items.product_id"))
#     tagid = db.Column(db.Integer, db.ForeignKey("tags.tag_id"))

ItemTags = db.Table(
    "ItemTags",
    db.Column("id", db.Integer, primary_key=True),
    db.Column("itemid", db.Integer, db.ForeignKey("items.product_id")),
    db.Column("tagid", db.Integer, db.ForeignKey("tags.tag_id"))
)
