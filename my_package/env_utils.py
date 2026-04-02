from typeguard import typechecked  # type: ignore


@typechecked
def env_flag(value: str) -> bool:
    """Compute env flag for this workflow.

    Args:
        value (str): Value for value.

    Returns:
        bool: True when the condition is met; otherwise False.
    """
    normalized = str(value).strip().lower()
    return normalized in {"1", "true", "yes", "on"}
