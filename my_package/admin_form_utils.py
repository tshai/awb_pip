from typeguard import typechecked  # type: ignore


@typechecked
def normalize_system_promte_view(view_input: str) -> str:
    normalized = str(view_input).strip().lower()
    if normalized == "archive":
        return "archive"
    return "active"


@typechecked
def safe_positive_int(value: str, fallback: int) -> int:
    try:
        parsed = int(str(value).strip())
        if parsed > 0:
            return parsed
    except (TypeError, ValueError):
        pass
    return fallback


@typechecked
def datetime_to_local_input(value: object) -> str:
    if value is None:
        return ""
    text = str(value).strip()
    if not text:
        return ""
    normalized = text.replace("T", " ")
    if len(normalized) < 16:
        return ""
    return normalized[:16].replace(" ", "T")


@typechecked
def normalize_datetime_local_input(raw_value: str) -> str:
    value = str(raw_value or "").strip()
    if not value:
        return ""
    normalized = value.replace("T", " ")
    if len(normalized) == 16:
        normalized += ":00"
    if len(normalized) != 19:
        raise ValueError("Invalid datetime format")
    return normalized


@typechecked
def safe_int_from_form(value: object, default_value: int) -> int:
    try:
        return int(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return default_value


@typechecked
def safe_float_from_form(value: object, default_value: float) -> float:
    try:
        return float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return default_value
