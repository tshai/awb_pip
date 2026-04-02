from typeguard import typechecked  # type: ignore


@typechecked
def qname(name: str) -> str:
    """Compute qname for this workflow.

    Args:
        name (str): Value for name.

    Returns:
        str: String result produced by this function.
    """
    return "`" + name.replace("`", "``") + "`"


@typechecked
def qstr(value: str) -> str:
    """Compute qstr for this workflow.

    Args:
        value (str): Value for value.

    Returns:
        str: String result produced by this function.
    """
    return "'" + value.replace("\\", "\\\\").replace("'", "\\'") + "'"


@typechecked
def is_target_column(col_name: str) -> bool:
    """Return whether target column is true for the given input.

    Args:
        col_name (str): Value for col name.

    Returns:
        bool: True when the condition is met; otherwise False.
    """
    return col_name == "id" or col_name.endswith("_id")


@typechecked
def already_big_unsigned(col_type: str) -> bool:
    """Compute already big unsigned for this workflow.

    Args:
        col_type (str): Value for col type.

    Returns:
        bool: True when the condition is met; otherwise False.
    """
    normalized = " ".join(col_type.lower().split())
    return normalized.startswith("bigint") and "unsigned" in normalized
