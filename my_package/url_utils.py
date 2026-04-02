from urllib.parse import urljoin, urlparse, urlunparse

from bs4 import BeautifulSoup
from typeguard import typechecked  # type: ignore


@typechecked
def ensure_http_url(raw_url: str) -> str:
    """Ensure http url satisfies required constraints.

    Args:
        raw_url (str): Raw input value for url.

    Returns:
        str: String result produced by this function.
    """
    cleaned = raw_url.strip()
    if not cleaned:
        raise ValueError("start_url is required")

    parsed = urlparse(cleaned)
    if not parsed.scheme:
        cleaned = f"https://{cleaned}"
        parsed = urlparse(cleaned)

    if parsed.scheme not in {"http", "https"}:
        raise ValueError("start_url must use http or https")
    if not parsed.netloc:
        raise ValueError("start_url must include a valid host")

    normalized = parsed._replace(fragment="")
    return urlunparse(normalized)


@typechecked
def normalize_url(raw_url: str) -> str:
    """Normalize url into a consistent format.

    Args:
        raw_url (str): Raw input value for url.

    Returns:
        str: String result produced by this function.
    """
    parsed = urlparse(raw_url)
    if not parsed.scheme or not parsed.netloc:
        raise ValueError("URL normalization requires an absolute URL")

    path = parsed.path or "/"
    if path != "/" and path.endswith("/"):
        path = path[:-1]

    normalized = parsed._replace(
        scheme=parsed.scheme.lower(),
        netloc=parsed.netloc.lower(),
        path=path,
        fragment="",
    )
    return urlunparse(normalized)


@typechecked
def extract_links(current_url: str, html: str, base_netloc: str) -> tuple[list[str], list[str]]:
    """Extract links from the provided data.

    Args:
        current_url (str): URL or link value used by this function.
        html (str): HTML content or fragment to process.
        base_netloc (str): Value for base netloc.

    Returns:
        tuple[list[str], list[str]]: List containing computed output items.
    """
    soup = BeautifulSoup(html, "html.parser")
    internal_links: list[str] = []
    external_links: list[str] = []
    seen_internal: set[str] = set()
    seen_external: set[str] = set()

    for anchor in soup.select("a[href]"):
        href = str(anchor.get("href") or "").strip()
        if not href:
            continue

        lowered = href.lower()
        if lowered.startswith("javascript:") or lowered.startswith("mailto:") or lowered.startswith("tel:"):
            continue

        resolved = urljoin(current_url, href)
        parsed = urlparse(resolved)
        if parsed.scheme not in {"http", "https"}:
            continue

        normalized = normalize_url(urlunparse(parsed._replace(fragment="")))
        if parsed.netloc.lower() == base_netloc:
            if normalized not in seen_internal:
                seen_internal.add(normalized)
                internal_links.append(normalized)
        else:
            if normalized not in seen_external:
                seen_external.add(normalized)
                external_links.append(normalized)

    return internal_links, external_links
