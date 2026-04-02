import re

from typeguard import typechecked  # type: ignore

_ENDPOINT_PATTERN = re.compile(r"^v1/[a-zA-Z0-9._/-]+$")
_GUID_PATTERN = re.compile(r"^[a-zA-Z0-9-]{1,64}$")


@typechecked
def validate_file_name(file_name: str) -> tuple[bool, str]:
    """Validate file name against expected rules.

    Args:
        file_name (str): File-system path or file name used by this function.

    Returns:
        tuple[bool, str]: Tuple containing computed output values.
    """
    file_name_stripped = str(file_name or "").strip()
    if not file_name_stripped:
        return False, "file_name is required"

    if not file_name_stripped.lower().endswith(".html"):
        return False, "file_name must have .html extension"

    base_name = file_name_stripped[:-5]
    if not re.match(r"^[a-zA-Z0-9_]+$", base_name):
        return (
            False,
            "file_name can only contain letters, numbers, and underscores (e.g., about.html, my_page.html)",
        )

    return True, ""


@typechecked
def is_valid_endpoint(endpoint: str) -> bool:
    """Return whether valid endpoint is true for the given input.

    Args:
        endpoint (str): Value for endpoint.

    Returns:
        bool: True when the condition is met; otherwise False.
    """
    endpoint_ref = str(endpoint or "").strip()
    if not endpoint_ref:
        return False
    if ".." in endpoint_ref or "//" in endpoint_ref:
        return False
    return bool(_ENDPOINT_PATTERN.fullmatch(endpoint_ref))


@typechecked
def safe_guid_for_path(value: str, fallback: str) -> str:
    """Compute safe guid for path for this workflow.

    Args:
        value (str): Value for value.
        fallback (str): Value for fallback.

    Returns:
        str: String result produced by this function.
    """
    value_ref = str(value or "").strip()
    if _GUID_PATTERN.fullmatch(value_ref):
        return value_ref
    return fallback
