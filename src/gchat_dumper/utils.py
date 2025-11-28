from datetime import datetime, timezone
from typing import Optional


def parse_iso8601(value: str) -> datetime:
    """Parse ISO 8601 date or datetime.

    - If time is missing, assume UTC midnight.
    - If timezone missing, assume UTC.
    """
    v = value.strip()
    # Try full datetime with timezone
    try:
        dt = datetime.fromisoformat(v.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except ValueError:
        pass

    # Try date only
    try:
        d = datetime.strptime(v, "%Y-%m-%d")
        return d.replace(tzinfo=timezone.utc)
    except ValueError as exc:
        raise ValueError(f"Cannot parse date/datetime '{value}'") from exc


def to_rfc3339_utc(dt: datetime) -> str:
    """Convert datetime to RFC3339 UTC string with Z suffix."""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    dt = dt.astimezone(timezone.utc)
    return dt.isoformat().replace("+00:00", "Z")


def safe_parse_datetime(value: Optional[str]):
    """Try to parse datetime string; return None on failure or missing value."""
    if not value:
        return None
    try:
        return parse_iso8601(value)
    except Exception:
        return None
