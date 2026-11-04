import csv
import io
import math
import re
from typing import Any

MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024
MAX_RECORDS = 5_000
MAX_COLUMNS = 50


def _convert_value(value: str | None) -> str | int | float | None:
    """Normalize a CSV cell while preserving non-numeric text."""
    if value is None:
        return None

    value = value.strip()

    if not value:
        return None

    # Preserve identifiers such as 00123.
    if re.fullmatch(r"[+-]?\d+", value):
        digits = value.lstrip("+-")
        if len(digits) > 1 and digits.startswith("0"):
            return value
        return int(value)

    try:
        number = float(value)
    except ValueError:
        return value

    if not math.isfinite(number):
        raise ValueError(f"Non-finite numeric value found: {value}")

    return number


def parse_csv(content: bytes) -> list[dict[str, Any]]:
    """Parse and validate a UTF-8 CSV file."""
    if not content:
        raise ValueError("The uploaded CSV file is empty.")

    if len(content) > MAX_FILE_SIZE_BYTES:
        raise ValueError("The CSV file exceeds the 5 MB size limit.")

    try:
        text = content.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ValueError("The CSV file must use UTF-8 encoding.") from exc

    try:
        reader = csv.DictReader(
            io.StringIO(text, newline=""),
            strict=True,
        )

        if not reader.fieldnames:
            raise ValueError("The CSV file must contain a header row.")

        headers = [header.strip() for header in reader.fieldnames]

        if any(not header for header in headers):
            raise ValueError("CSV column names must not be empty.")

        normalized_headers = [header.casefold() for header in headers]

        if len(normalized_headers) != len(set(normalized_headers)):
            raise ValueError("Duplicate CSV column names are not allowed.")

        if len(headers) > MAX_COLUMNS:
            raise ValueError(f"The CSV file must not exceed {MAX_COLUMNS} columns.")

        reader.fieldnames = headers
        records: list[dict[str, Any]] = []

        for row in reader:
            if row.get(None) is not None:
                raise ValueError("A CSV row contains more values than the header.")

            if len(records) >= MAX_RECORDS:
                raise ValueError(f"The CSV file must not exceed {MAX_RECORDS} records.")

            record = {header: _convert_value(row.get(header)) for header in headers}

            records.append(record)

    except csv.Error as exc:
        raise ValueError("The CSV file has an invalid structure.") from exc

    if not records:
        raise ValueError("The CSV file must contain at least one data row.")

    return records
