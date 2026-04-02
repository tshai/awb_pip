import os
from datetime import datetime, timezone
from typing import Any

from typeguard import typechecked  # type: ignore


@typechecked
def request_timeout_seconds() -> int:
    raw = str(os.getenv("GOOGLE_API_TIMEOUT_SECONDS") or "20").strip()
    try:
        parsed = int(raw)
    except (TypeError, ValueError):
        parsed = 20
    return max(5, min(parsed, 120))


@typechecked
def clean_scope_string(scope_string: str) -> str:
    value = str(scope_string or "").strip()
    if not value:
        return ""
    tokens = [item.strip() for item in value.split() if item.strip()]
    dedupe: list[str] = []
    seen: set[str] = set()
    for token in tokens:
        if token in seen:
            continue
        seen.add(token)
        dedupe.append(token)
    return " ".join(dedupe)


@typechecked
def safe_token_response_metadata(token_data: Any) -> str:
    if not isinstance(token_data, dict):
        return f"type={type(token_data).__name__}"
    keys = sorted(str(key) for key in token_data.keys())
    return f"keys={keys}"


@typechecked
def extract_suffix_id(resource_name: str, prefix: str) -> str:
    value = str(resource_name or "").strip()
    if not value:
        return ""
    expected_prefix = f"{prefix}/"
    if value.startswith(expected_prefix):
        return value[len(expected_prefix) :]
    return value


@typechecked
def utc_now_naive() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


@typechecked
def normalize_token_expiry_utc_naive(raw_value: Any) -> datetime | None:
    if isinstance(raw_value, datetime):
        if raw_value.tzinfo is None:
            return raw_value
        return raw_value.astimezone(timezone.utc).replace(tzinfo=None)

    value = str(raw_value or "").strip()
    if not value:
        return None

    normalized = value
    if normalized.endswith("Z"):
        normalized = f"{normalized[:-1]}+00:00"

    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return None

    if parsed.tzinfo is None:
        return parsed
    return parsed.astimezone(timezone.utc).replace(tzinfo=None)
