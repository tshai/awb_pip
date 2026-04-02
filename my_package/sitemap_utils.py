from urllib.parse import quote

from typeguard import typechecked  # type: ignore


@typechecked
def normalize_public_base_url(public_base_url: str) -> str:
    """Normalize public base url into a consistent format.

    Args:
        public_base_url (str): URL or link value used by this function.

    Returns:
        str: String result produced by this function.
    """
    normalized = str(public_base_url or "").strip()
    if not normalized:
        raise ValueError("missing_public_base_url")
    if not normalized.lower().startswith(("http://", "https://")):
        normalized = f"https://{normalized}"
    return normalized.rstrip("/")


@typechecked
def build_public_url(public_base_url: str, relative_path: str) -> str:
    """Build public url from the provided inputs.

    Args:
        public_base_url (str): URL or link value used by this function.
        relative_path (str): File-system path or file name used by this function.

    Returns:
        str: String result produced by this function.
    """
    normalized_relative_path = str(relative_path or "").strip().replace("\\", "/")
    if not normalized_relative_path:
        raise ValueError("missing_relative_path")

    path_parts = [quote(part) for part in normalized_relative_path.split("/") if part]
    encoded_path = "/".join(path_parts)

    if normalized_relative_path.lower() == "index.html":
        return f"{public_base_url}/"

    if normalized_relative_path.lower().endswith("/index.html"):
        trimmed_path = encoded_path[: -len("index.html")]
        return f"{public_base_url}/{trimmed_path}"

    return f"{public_base_url}/{encoded_path}"
