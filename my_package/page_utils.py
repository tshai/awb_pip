import re

from typeguard import typechecked  # type: ignore


@typechecked
def to_bool(value: object) -> bool:
    """Convert bool into the target representation.

    Args:
        value (object): Value for value.

    Returns:
        bool: True when the condition is met; otherwise False.
    """
    normalized = str(value or "").strip().lower()
    return normalized in {"1", "true", "yes", "on"}


@typechecked
def normalize_page_file_name(page_name: str, protected_page_files: set[str]) -> str:
    """Normalize page file name into a consistent format.

    Args:
        page_name (str): Value for page name.
        protected_page_files (set[str]): File-system path or file name used by this function.

    Returns:
        str: String result produced by this function.
    """
    normalized_name = re.sub(r"\s+", " ", str(page_name or "").strip())
    if not normalized_name:
        raise ValueError("Page name is required.")
    if len(normalized_name) > 20:
        raise ValueError("Page name must be up to 20 characters.")
    if "." in normalized_name:
        raise ValueError("Use page name only (for example: shipping), without file extension.")

    slug = re.sub(r"\s+", "_", normalized_name).strip("_")
    slug = re.sub(r"[^\w]", "_", slug, flags=re.UNICODE)
    slug = re.sub(r"_+", "_", slug).strip("_")
    slug = slug.lower()
    if not slug:
        raise ValueError("Page name is invalid after normalization.")

    file_name = f"{slug}.html"
    protected = {str(item).lower() for item in protected_page_files}
    if file_name.lower() in protected:
        raise ValueError(f"Page name '{slug}' is reserved and cannot be used.")
    return file_name
