from typeguard import typechecked  # type: ignore


@typechecked
def parse_bool_flag(raw_value: str) -> bool:
    """Parse bool flag into a structured Python value.

    Args:
        raw_value (str): Raw input value for value.

    Returns:
        bool: True when the condition is met; otherwise False.
    """
    normalized = raw_value.strip().lower()
    if normalized == "true":
        return True
    if normalized == "false":
        return False
    raise ValueError("run-llm must be true or false")
