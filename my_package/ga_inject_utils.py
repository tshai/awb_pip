import re

from typeguard import typechecked  # type: ignore

GA4_MANAGED_BLOCK_START = "<!-- AWB_GA4_START -->"
GA4_MANAGED_BLOCK_END = "<!-- AWB_GA4_END -->"
GA4_MEASUREMENT_ID_RE = re.compile(r"^G-[A-Z0-9]+$")


@typechecked
def normalize_legacy_script_closings(content: str) -> str:
    """Normalize legacy script closings into a consistent format.

    Args:
        content (str): Value for content.

    Returns:
        str: String result produced by this function.
    """
    current = str(content or "")
    if not current:
        return ""
    return re.sub(r"<\\/\s*script\s*>", "</script>", current, flags=re.IGNORECASE)


@typechecked
def contains_legacy_script_closings(content: str) -> bool:
    """Compute contains legacy script closings for this workflow.

    Args:
        content (str): Value for content.

    Returns:
        bool: True when the condition is met; otherwise False.
    """
    current = str(content or "")
    if not current:
        return False
    return bool(re.search(r"<\\/\s*script\s*>", current, flags=re.IGNORECASE))


@typechecked
def normalize_ga4_measurement_id(value: str) -> str:
    """Normalize ga4 measurement id into a consistent format.

    Args:
        value (str): Value for value.

    Returns:
        str: String result produced by this function.
    """
    normalized = str(value or "").strip().upper()
    if GA4_MEASUREMENT_ID_RE.fullmatch(normalized):
        return normalized
    return ""


@typechecked
def replace_managed_block(content: str, start_marker: str, end_marker: str, new_block: str) -> str:
    """Compute replace managed block for this workflow.

    Args:
        content (str): Value for content.
        start_marker (str): Value for start marker.
        end_marker (str): Value for end marker.
        new_block (str): Value for new block.

    Returns:
        str: String result produced by this function.
    """
    current = str(content or "")
    start = str(start_marker or "")
    end = str(end_marker or "")
    replacement = str(new_block or "")
    if not start or not end:
        return current

    start_index = current.find(start)
    end_index = current.find(end)

    if start_index != -1 and end_index != -1 and end_index >= start_index:
        end_index += len(end)
        prefix = current[:start_index].rstrip()
        suffix = current[end_index:].lstrip("\n")
        if replacement:
            if prefix:
                return f"{prefix}\n\n{replacement}\n{suffix}".rstrip() + ("\n" if suffix else "")
            return f"{replacement}\n{suffix}".rstrip() + ("\n" if suffix else "")
        if prefix and suffix:
            return f"{prefix}\n{suffix}".rstrip() + "\n"
        return (prefix or suffix).rstrip() + ("\n" if (prefix or suffix) else "")

    if not replacement:
        return current
    if not current.strip():
        return replacement + "\n"
    return current.rstrip() + "\n\n" + replacement + "\n"


@typechecked
def build_ga4_head_inject_block(measurement_id: str) -> str:
    """Build ga4 head inject block from the provided inputs.

    Args:
        measurement_id (str): Identifier for measurement.

    Returns:
        str: String result produced by this function.
    """
    measurement = normalize_ga4_measurement_id(measurement_id)
    if not measurement:
        raise ValueError("Invalid GA4 measurement ID")

    return (
        f"{GA4_MANAGED_BLOCK_START}\n"
        "<script async src=\"https://www.googletagmanager.com/gtag/js?id="
        f"{measurement}\"></script>\n"
        "<script>\n"
        "  window.dataLayer = window.dataLayer || [];\n"
        "  function gtag(){dataLayer.push(arguments);}\n"
        "  gtag('js', new Date());\n"
        f"  gtag('config', '{measurement}');\n"
        "</script>\n"
        f"{GA4_MANAGED_BLOCK_END}"
    )


@typechecked
def content_has_measurement_code(content: str, measurement_id: str) -> bool:
    """Compute content has measurement code for this workflow.

    Args:
        content (str): Value for content.
        measurement_id (str): Identifier for measurement.

    Returns:
        bool: True when the condition is met; otherwise False.
    """
    normalized_measurement_id = normalize_ga4_measurement_id(measurement_id)
    if not normalized_measurement_id:
        return False

    normalized_content = str(content or "").lower()
    measurement_marker = f"gtag/js?id={normalized_measurement_id}".lower()
    config_single_quote_marker = f"gtag('config', '{normalized_measurement_id}');".lower()
    config_double_quote_marker = f'gtag("config", "{normalized_measurement_id}");'.lower()
    return measurement_marker in normalized_content and (
        config_single_quote_marker in normalized_content
        or config_double_quote_marker in normalized_content
    )


@typechecked
def insert_managed_block_before_head_close(content: str, managed_block: str) -> str:
    """Compute insert managed block before head close for this workflow.

    Args:
        content (str): Value for content.
        managed_block (str): Value for managed block.

    Returns:
        str: String result produced by this function.
    """
    current = str(content or "")
    block = str(managed_block or "").strip()
    if not block:
        return current

    if GA4_MANAGED_BLOCK_START in current and GA4_MANAGED_BLOCK_END in current:
        return replace_managed_block(current, GA4_MANAGED_BLOCK_START, GA4_MANAGED_BLOCK_END, block)

    if block in current:
        return current

    if "googletagmanager.com/gtag/js?id=" in current:
        normalized_block = block.lower()
        if normalized_block.find("gtag/js?id=") != -1:
            marker = normalized_block.split("gtag/js?id=", 1)[1].split("\"", 1)[0].split("'", 1)[0]
            if marker and marker.lower() in current.lower():
                return current

    lower_current = current.lower()
    closing_head_index = lower_current.find("</head>")
    if closing_head_index >= 0:
        prefix = current[:closing_head_index].rstrip()
        suffix = current[closing_head_index:]
        if prefix:
            return f"{prefix}\n{block}\n{suffix}"
        return f"{block}\n{suffix}"

    if not current.strip():
        return f"{block}\n"
    return f"{current.rstrip()}\n\n{block}\n"
