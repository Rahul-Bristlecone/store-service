import pytest
from marshmallow import ValidationError

from src.store_service.schemas.store_schema import StoreSchema


def test_store_schema_requires_customer_name():
    schema = StoreSchema()

    with pytest.raises(ValidationError) as exc_info:
        schema.load({"store_number": 1, "store_name": "Main"})

    assert "customer_name" in exc_info.value.messages


def test_store_schema_rejects_dump_only_fields_on_load():
    schema = StoreSchema()

    payload = {
        "store_id": 99,
        "user_id": 7,
        "store_number": 123,
        "store_name": "Central",
        "customer_name": "Alice",
    }
    with pytest.raises(ValidationError) as exc_info:
        schema.load(payload)

    assert exc_info.value.messages["store_id"] == ["Unknown field."]
    assert exc_info.value.messages["user_id"] == ["Unknown field."]
