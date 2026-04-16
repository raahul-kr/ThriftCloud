"""
File parser for ThriftCloud.

Supports CSV, TXT, and JSON billing file uploads.
Parses uploaded files into a normalized {service: cost} dictionary.
"""

import csv
import io
import json
from pathlib import Path


ALLOWED_EXTENSIONS = {".csv", ".txt", ".json"}

SERVICE_COLUMN_NAMES = (
    "service", "resource", "product", "service_name",
    "servicename", "product_name", "productname",
    "metercategory", "line_item_product_code",
)

COST_COLUMN_NAMES = (
    "cost", "amount", "total_cost", "totalcost",
    "charge", "blendedcost", "unblendedcost",
    "pretaxcost", "extendedcost",
)


class ParseError(ValueError):
    """Raised when a billing file cannot be parsed."""
    pass


def parse_file(file_bytes: bytes, filename: str) -> dict[str, float]:
    """
    Parse an uploaded billing file into a {service: cost} dictionary.

    Supported formats:
    - CSV/TXT with header row containing service and cost columns
    - JSON object: {"billing_data": {"EC2": 1300}}
    - JSON array: [{"service": "EC2", "cost": 1300}]

    Args:
        file_bytes: Raw bytes of the uploaded file.
        filename: Original filename (used to determine format).

    Returns:
        Dictionary mapping service names to costs.

    Raises:
        ParseError: If the file cannot be parsed.
    """
    if not filename:
        raise ParseError("Uploaded file must have a filename.")

    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        allowed = ", ".join(sorted(ALLOWED_EXTENSIONS))
        raise ParseError(f"Unsupported file type '{ext}'. Allowed: {allowed}.")

    if not file_bytes:
        raise ParseError("Uploaded file is empty.")

    text = file_bytes.decode("utf-8-sig")

    if ext in (".csv", ".txt"):
        return _parse_delimited(text)
    else:
        return _parse_json(text)


def _parse_delimited(text: str) -> dict[str, float]:
    """Parse CSV or TXT with header row."""
    sample = text[:4096]
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=",;\t|")
    except csv.Error:
        dialect = csv.excel

    reader = csv.DictReader(io.StringIO(text), dialect=dialect)
    if not reader.fieldnames:
        raise ParseError("CSV/TXT file must include a header row.")

    service_col = _find_column(reader.fieldnames, SERVICE_COLUMN_NAMES)
    cost_col = _find_column(reader.fieldnames, COST_COLUMN_NAMES)

    if not service_col or not cost_col:
        raise ParseError(
            "Could not identify service and cost columns. "
            "Include headers like: service,cost"
        )

    totals: dict[str, float] = {}
    for row in reader:
        service = _clean_text(row.get(service_col))
        if not service:
            continue
        amount = _safe_float(row.get(cost_col))
        if amount <= 0:
            continue
        totals[service] = round(totals.get(service, 0.0) + amount, 2)

    if not totals:
        raise ParseError("No billable rows found in file.")
    return totals


def _parse_json(text: str) -> dict[str, float]:
    """Parse JSON billing data."""
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ParseError(f"Invalid JSON: {exc.msg}") from exc

    if isinstance(payload, dict):
        # Format: {"billing_data": {"EC2": 1300}}
        if isinstance(payload.get("billing_data"), dict):
            return _coerce_cost_map(payload["billing_data"])

        # Format: {"rows": [...]} or similar
        for key in ("rows", "records", "items", "data"):
            if isinstance(payload.get(key), list):
                return _rows_to_map(payload[key])

        # Format: {"EC2": 1300, "S3": 400}
        return _coerce_cost_map(payload)

    if isinstance(payload, list):
        # Format: [{"service": "EC2", "cost": 1300}]
        return _rows_to_map(payload)

    raise ParseError("JSON must be an object or array.")


def _rows_to_map(rows: list) -> dict[str, float]:
    """Convert array of row objects to cost map."""
    if not rows:
        raise ParseError("JSON array is empty.")
    if not all(isinstance(r, dict) for r in rows):
        raise ParseError("JSON array items must be objects.")

    keys = list(rows[0].keys())
    service_col = _find_column(keys, SERVICE_COLUMN_NAMES)
    cost_col = _find_column(keys, COST_COLUMN_NAMES)

    if not service_col or not cost_col:
        raise ParseError(
            "JSON rows must have service and cost fields. "
            "Example: {\"service\": \"EC2\", \"cost\": 1300}"
        )

    totals: dict[str, float] = {}
    for row in rows:
        service = _clean_text(row.get(service_col))
        if not service:
            continue
        amount = _safe_float(row.get(cost_col))
        if amount <= 0:
            continue
        totals[service] = round(totals.get(service, 0.0) + amount, 2)

    if not totals:
        raise ParseError("No billable rows found in JSON.")
    return totals


def _coerce_cost_map(data: dict) -> dict[str, float]:
    """Convert a {service: cost} dict, validating values."""
    totals: dict[str, float] = {}
    for service, value in data.items():
        name = _clean_text(service)
        amount = _safe_float(value)
        if not name or amount <= 0:
            continue
        totals[name] = round(totals.get(name, 0.0) + amount, 2)

    if not totals:
        raise ParseError("No valid service/cost pairs found.")
    return totals


def _find_column(fieldnames: list[str], candidates: tuple[str, ...]) -> str | None:
    """Find a matching column name from candidates."""
    normalized = {name.strip().lower(): name for name in fieldnames if name}
    for candidate in candidates:
        if candidate in normalized:
            return normalized[candidate]
    return None


def _clean_text(value) -> str:
    """Safely convert value to stripped string."""
    if value is None:
        return ""
    return str(value).strip()


def _safe_float(value) -> float:
    """Safely convert value to float, handling currency symbols."""
    if value is None:
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip().replace(",", "")
    for prefix in ("$", "₹", "€", "£"):
        if text.startswith(prefix):
            text = text[len(prefix):]
    try:
        return float(text)
    except ValueError:
        return 0.0
