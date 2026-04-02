import re

from bs4 import BeautifulSoup
from typeguard import typechecked  # type: ignore


@typechecked
def normalize_href_path(href: str) -> str:
    """Normalize href path into a consistent format.

    Args:
        href (str): URL or link value used by this function.

    Returns:
        str: String result produced by this function.
    """
    normalized = str(href or "").strip().lower().replace("\\", "/")
    while normalized.startswith("./"):
        normalized = normalized[2:]
    normalized = normalized.lstrip("/")
    if normalized.endswith("/"):
        normalized = normalized[:-1]
    return normalized


@typechecked
def next_anchor_data_ai_id(soup: BeautifulSoup) -> str:
    """Compute next anchor data ai id for this workflow.

    Args:
        soup (BeautifulSoup): Value for soup.

    Returns:
        str: String result produced by this function.
    """
    max_id = 0
    for anchor in soup.find_all("a", attrs={"data-ai-id": True}):
        raw_id = str(anchor.get("data-ai-id") or "").strip().lower()
        match = re.match(r"^a(\d+)$", raw_id)
        if not match:
            continue
        current = int(match.group(1))
        if current > max_id:
            max_id = current
    return f"a{max_id + 1}"
