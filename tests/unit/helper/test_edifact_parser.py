from src.store_service.helper.edifact_parser import parse_edifact


def test_parse_edifact_parses_segments(tmp_path):
    edi_file = tmp_path / "sample.edi"
    edi_file.write_text("UNH+1+ORDERS:D:96A:UN'BGM+220+2+9'CUX+2:INR:9'", encoding="utf-8")

    parsed = parse_edifact(str(edi_file))

    assert parsed["UNH"] == ["UNH", "1", "ORDERS:D:96A:UN"]
    assert parsed["BGM"] == ["BGM", "220", "2", "9"]
    assert parsed["CUX"] == ["CUX", "2:INR:9"]


def test_parse_edifact_ignores_empty_segments(tmp_path):
    edi_file = tmp_path / "sample_with_empty_segments.edi"
    edi_file.write_text("BGM+220+2+9''\n  'PRI+AAA:1499.50'", encoding="utf-8")

    parsed = parse_edifact(str(edi_file))

    assert set(parsed.keys()) == {"BGM", "PRI"}
