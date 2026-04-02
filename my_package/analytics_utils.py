from typing import Any
from urllib.parse import urlparse

from typeguard import typechecked  # type: ignore


@typechecked
def normalize_connect_mode(value: str) -> str:
    normalized = str(value or "").strip().lower()
    if normalized == "create":
        return "create"
    return "existing"


@typechecked
def is_valid_http_url(value: str) -> bool:
    raw = str(value or "").strip()
    if not raw:
        return False
    parsed = urlparse(raw)
    if parsed.scheme not in {"http", "https"}:
        return False
    return bool(parsed.netloc)


@typechecked
def scope_tokens(scope_string: str) -> set[str]:
    tokens = str(scope_string or "").split()
    return {token.strip() for token in tokens if token.strip()}


@typechecked
def safe_int(value: Any) -> int:
    raw = str(value or "").strip()
    if not raw:
        return 0
    try:
        return int(float(raw))
    except (TypeError, ValueError):
        return 0


@typechecked
def safe_float(value: Any) -> float:
    raw = str(value or "").strip()
    if not raw:
        return 0.0
    try:
        return float(raw)
    except (TypeError, ValueError):
        return 0.0


@typechecked
def to_percent(value: float) -> float:
    if value <= 1.0:
        return value * 100.0
    return value


@typechecked
def format_ga_date(raw_value: str) -> str:
    value = str(raw_value or "").strip()
    if len(value) == 8 and value.isdigit():
        return f"{value[0:4]}-{value[4:6]}-{value[6:8]}"
    return value
