from typeguard import typechecked  # type: ignore


@typechecked
def normalize_system_promte_view(view_input: str) -> str:
    """Normalize system promte view into a consistent format.

    Args:
        view_input (str): Value for view input.

    Returns:
        str: String result produced by this function.
    """
    normalized = str(view_input).strip().lower()
    if normalized == "archive":
        return "archive"
    return "active"


@typechecked
def safe_positive_int(value: str, fallback: int) -> int:
    """Compute safe positive int for this workflow.

    Args:
        value (str): Value for value.
        fallback (int): Value for fallback.

    Returns:
        int: Integer result produced by this function.
    """
    try:
        parsed = int(str(value).strip())
        if parsed > 0:
            return parsed
    except (TypeError, ValueError):
        pass
    return fallback


@typechecked
def datetime_to_local_input(value: object) -> str:
    """Compute datetime to local input for this workflow.

    Args:
        value (object): Value for value.

    Returns:
        str: String result produced by this function.
    """
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
    """Normalize datetime local input into a consistent format.

    Args:
        raw_value (str): Raw input value for value.

    Returns:
        str: String result produced by this function.
    """
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
    """Compute safe int from form for this workflow.

    Args:
        value (object): Value for value.
        default_value (int): Value for default value.

    Returns:
        int: Integer result produced by this function.
    """
    try:
        return int(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return default_value


@typechecked
def safe_float_from_form(value: object, default_value: float) -> float:
    """Compute safe float from form for this workflow.

    Args:
        value (object): Value for value.
        default_value (float): Value for default value.

    Returns:
        float: Floating-point result produced by this function.
    """
    try:
        return float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return default_value
