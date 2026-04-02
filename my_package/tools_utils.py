from typing import Any

from typeguard import typechecked  # type: ignore


@typechecked
def deep_merge_dicts(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    """Compute deep merge dicts for this workflow.

    Args:
        base (dict[str, Any]): Value for base.
        override (dict[str, Any]): Value for override.

    Returns:
        dict[str, Any]: Dictionary containing computed output values.
    """
    merged: dict[str, Any] = dict(base)
    for key, value in override.items():
        if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
            merged[key] = deep_merge_dicts(merged[key], value)
        else:
            merged[key] = value
    return merged


@typechecked
def json_object_pairs_merge(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    """Compute json object pairs merge for this workflow.

    Args:
        pairs (list[tuple[str, Any]]): Value for pairs.

    Returns:
        dict[str, Any]: Dictionary containing computed output values.
    """
    merged: dict[str, Any] = {}
    for key, value in pairs:
        if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
            merged[key] = deep_merge_dicts(merged[key], value)
        else:
            merged[key] = value
    return merged


@typechecked
def mask_id_xor_value(id_value: int, secret: int) -> int:
    """Compute mask id xor value for this workflow.

    Args:
        id_value (int): Value for id value.
        secret (int): Value for secret.

    Returns:
        int: Integer result produced by this function.
    """
    return id_value ^ secret


@typechecked
def unmask_id_xor_value(masked_value: int, secret: int) -> int:
    """Compute unmask id xor value for this workflow.

    Args:
        masked_value (int): Value for masked value.
        secret (int): Value for secret.

    Returns:
        int: Integer result produced by this function.
    """
    return masked_value ^ secret


@typechecked
def remove_empty_lines_text(text: str) -> str:
    """Remove empty lines text from the provided input.

    Args:
        text (str): Value for text.

    Returns:
        str: String result produced by this function.
    """
    return "\n".join(line for line in text.splitlines() if line.strip())
