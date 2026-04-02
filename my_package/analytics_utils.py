from typing import Any
from urllib.parse import urlparse

from typeguard import typechecked  # type: ignore


@typechecked
def normalize_connect_mode(value: str) -> str:
    """Normalize connect mode into a consistent format.

    Args:
        value (str): Value for value.

    Returns:
        str: String result produced by this function.
    """
    normalized = str(value or "").strip().lower()
    if normalized == "create":
        return "create"
    return "existing"


@typechecked
def is_valid_http_url(value: str) -> bool:
    """Return whether valid http url is true for the given input.

    Args:
        value (str): Value for value.

    Returns:
        bool: True when the condition is met; otherwise False.
    """
    raw = str(value or "").strip()
    if not raw:
        return False
    parsed = urlparse(raw)
    if parsed.scheme not in {"http", "https"}:
        return False
    return bool(parsed.netloc)


@typechecked
def scope_tokens(scope_string: str) -> set[str]:
    """Compute scope tokens for this workflow.

    Args:
        scope_string (str): Value for scope string.

    Returns:
        set[str]: Computed result from this function.
    """
    tokens = str(scope_string or "").split()
    return {token.strip() for token in tokens if token.strip()}


@typechecked
def safe_int(value: Any) -> int:
    """Compute safe int for this workflow.

    Args:
        value (Any): Value for value.

    Returns:
        int: Integer result produced by this function.
    """
    raw = str(value or "").strip()
    if not raw:
        return 0
    try:
        return int(float(raw))
    except (TypeError, ValueError):
        return 0


@typechecked
def safe_float(value: Any) -> float:
    """Compute safe float for this workflow.

    Args:
        value (Any): Value for value.

    Returns:
        float: Floating-point result produced by this function.
    """
    raw = str(value or "").strip()
    if not raw:
        return 0.0
    try:
        return float(raw)
    except (TypeError, ValueError):
        return 0.0


@typechecked
def to_percent(value: float) -> float:
    """Convert percent into the target representation.

    Args:
        value (float): Value for value.

    Returns:
        float: Floating-point result produced by this function.
    """
    if value <= 1.0:
        return value * 100.0
    return value


@typechecked
def format_ga_date(raw_value: str) -> str:
    """Format ga date for output or display.

    Args:
        raw_value (str): Raw input value for value.

    Returns:
        str: String result produced by this function.
    """
    value = str(raw_value or "").strip()
    if len(value) == 8 and value.isdigit():
        return f"{value[0:4]}-{value[4:6]}-{value[6:8]}"
    return value
