from store_service.utils import edifact_transformer


def test_transform_edifact_to_json_maps_fields(monkeypatch):
    monkeypatch.setattr(
        edifact_transformer,
        "parse_edifact",
        lambda _file_path: {
            "BGM": ["BGM", "220", "2", "9"],
            "CUX": ["CUX", "2:USD:9"],
            "PRI": ["PRI", "AAA:1499.50"],
        },
    )

    result = edifact_transformer.transform_edifact_to_json("ignored-path.edi")

    assert result == {
        "store_number": 2,
        "order_status": "pending",
        "total_amount": 1499.50,
        "currency": "USD",
    }


def test_transform_edifact_to_json_uses_defaults(monkeypatch):
    monkeypatch.setattr(edifact_transformer, "parse_edifact", lambda _file_path: {})

    result = edifact_transformer.transform_edifact_to_json("ignored-path.edi")

    assert result == {
        "store_number": 0,
        "order_status": "pending",
        "total_amount": 0.0,
        "currency": "INR",
    }
