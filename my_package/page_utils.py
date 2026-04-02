import re

from typeguard import typechecked  # type: ignore


@typechecked
def to_bool(value: object) -> bool:
    normalized = str(value or "").strip().lower()
    return normalized in {"1", "true", "yes", "on"}


@typechecked
def normalize_page_file_name(page_name: str, protected_page_files: set[str]) -> str:
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
