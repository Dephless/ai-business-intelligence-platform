import pytest

from app.services.csv_service import parse_csv


def test_parse_csv_converts_numeric_values():
    content = b"product,revenue,quantity\nLaptop,1299.99,2\nMouse,29.99,5\n"

    records = parse_csv(content)

    assert len(records) == 2
    assert records[0]["product"] == "Laptop"
    assert records[0]["revenue"] == 1299.99
    assert records[0]["quantity"] == 2


def test_parse_csv_preserves_leading_zeros():
    content = b"customer_id,revenue\n00123,100\n"

    records = parse_csv(content)

    assert records[0]["customer_id"] == "00123"
    assert records[0]["revenue"] == 100


def test_parse_csv_rejects_empty_file():
    with pytest.raises(ValueError, match="empty"):
        parse_csv(b"")


def test_parse_csv_rejects_duplicate_headers():
    content = b"revenue,Revenue\n100,200\n"

    with pytest.raises(ValueError, match="Duplicate"):
        parse_csv(content)


def test_parse_csv_rejects_invalid_encoding():
    content = b"\xff\xfe\x00"

    with pytest.raises(ValueError, match="UTF-8"):
        parse_csv(content)


def test_parse_csv_rejects_extra_columns_in_row():
    content = b"name,revenue\nLaptop,100,extra\n"

    with pytest.raises(ValueError, match="more values"):
        parse_csv(content)


def test_parse_csv_handles_missing_and_empty_values():
    content = b"name,revenue\nLaptop,\nMouse\n"
    records = parse_csv(content)

    assert records == [
        {"name": "Laptop", "revenue": None},
        {"name": "Mouse", "revenue": None},
    ]


def test_parse_csv_rejects_missing_header():
    with pytest.raises(ValueError, match="header"):
        parse_csv(b"\n")


def test_parse_csv_rejects_empty_data():
    with pytest.raises(ValueError, match="at least one data row"):
        parse_csv(b"name,revenue\n")


@pytest.mark.parametrize("value", [b"NaN", b"Infinity", b"-Infinity"])
def test_parse_csv_rejects_non_finite_numbers(value):
    content = b"revenue\n" + value + b"\n"

    with pytest.raises(ValueError, match="Non-finite"):
        parse_csv(content)


def test_parse_csv_rejects_invalid_structure():
    content = b'name,revenue\n"unterminated,100\n'

    with pytest.raises(ValueError, match="invalid structure"):
        parse_csv(content)


def test_parse_csv_rejects_too_many_columns(monkeypatch):
    import app.services.csv_service as csv_service

    monkeypatch.setattr(csv_service, "MAX_COLUMNS", 1)

    with pytest.raises(ValueError, match="columns"):
        parse_csv(b"name,revenue\nLaptop,100\n")


def test_parse_csv_rejects_too_many_records(monkeypatch):
    import app.services.csv_service as csv_service

    monkeypatch.setattr(csv_service, "MAX_RECORDS", 1)

    with pytest.raises(ValueError, match="records"):
        parse_csv(b"name\nLaptop\nMouse\n")


def test_parse_csv_rejects_oversized_file(monkeypatch):
    import app.services.csv_service as csv_service

    monkeypatch.setattr(csv_service, "MAX_FILE_SIZE_BYTES", 5)

    with pytest.raises(ValueError, match="5 MB"):
        parse_csv(b"name,revenue\nLaptop,100\n")


def test_parse_csv_rejects_empty_header_name():
    with pytest.raises(ValueError, match="must not be empty"):
        parse_csv(b",revenue\nLaptop,100\n")
