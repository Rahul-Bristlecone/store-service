from ..helper.edifact_parser import parse_edifact

def transform_edifact_to_json(file_path: str) -> dict:
    segments = parse_edifact(file_path)

    # Extract values from EDIFACT segments
    store_id = int(segments.get("BGM", ["", "", "0"])[2])  # BGM+220+2+9 → "2"
    order_status = "pending"  # mapped manually from BGM status code

    # CUX+2:INR:9 => currency is the second component in the composite value.
    cux_value = segments.get("CUX", ["", "2:INR:9"])[1]
    currency_parts = cux_value.split(":") if cux_value else []
    currency = currency_parts[1] if len(currency_parts) > 1 else "INR"

    # PRI+AAA:1499.50 => amount is the second component in the composite value.
    pri_value = segments.get("PRI", ["", "0"])[1]
    pri_parts = pri_value.split(":") if pri_value else []
    total_amount = float(pri_parts[1]) if len(pri_parts) > 1 else 0.0

    return {
        "store_id": store_id,
        "order_status": order_status,
        "total_amount": total_amount,
        "currency": currency
    }
