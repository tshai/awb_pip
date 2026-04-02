from typeguard import typechecked  # type: ignore


@typechecked
def validate_filename_only(page_name: str) -> bool:
    """Validate filename only against expected rules.

    Args:
        page_name (str): Value for page name.

    Returns:
        bool: True when the condition is met; otherwise False.
    """
    if not isinstance(page_name, str) or not page_name.strip():
        return False
    if "/" in page_name or "\\" in page_name or ".." in page_name:
        return False
    return True


@typechecked
def should_include_file(file_name: str) -> bool:
    """Return whether include file should be applied.

    Args:
        file_name (str): File-system path or file name used by this function.

    Returns:
        bool: True when the condition is met; otherwise False.
    """
    if file_name.startswith("index_full") and file_name.endswith(".html"):
        return False
    if file_name == "design_blueprint.txt":
        return False
    return True
