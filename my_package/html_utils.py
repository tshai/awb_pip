import re
from typing import Any

from lxml import html
from lxml.etree import ParserError
from typeguard import typechecked  # type: ignore

VOID_TAGS = {"img", "meta", "link", "br", "hr", "input"}


@typechecked
def normalize_lxml_error(msg: str) -> dict[str, Any]:
    """Normalize lxml error into a consistent format.

    Args:
        msg (str): Value for msg.

    Returns:
        dict[str, Any]: Dictionary containing computed output values.
    """
    line = None
    column = None

    match = re.search(r"line\s+(\d+),\s*column\s+(\d+)", msg)
    if match:
        line = int(match.group(1))
        column = int(match.group(2))

    if "htmlParseEntityRef" in msg:
        friendly = "Invalid HTML entity. Did you forget a semicolon (;) after &entity?"
    else:
        friendly = msg

    return {
        "message": friendly.strip(),
        "raw": msg,
        "line": line,
        "column": column,
    }


@typechecked
def fix_common_entities(content: str) -> str:
    """Compute fix common entities for this workflow.

    Args:
        content (str): Value for content.

    Returns:
        str: String result produced by this function.
    """
    common_entities = [
        "nbsp", "copy", "reg", "deg", "euro", "pound", "yen", "cent",
        "amp", "lt", "gt", "quot", "apos", "bull", "middot", "hellip",
        "mdash", "ndash", "lsquo", "rsquo", "ldquo", "rdquo",
    ]

    for entity in common_entities:
        content = re.sub(
            rf"&{entity}(?!;)(?=\s|[a-zA-Z]|<|$)",
            f"&{entity};",
            content,
        )

    content = re.sub(
        r"&(?!([a-zA-Z]+|#\d+|#x[0-9a-fA-F]+);)",
        "&amp;",
        content,
    )
    return content


@typechecked
def find_unclosed_void_tags(content: str, tag: str) -> list[dict[str, Any]]:
    """Find unclosed void tags within the input data.

    Args:
        content (str): Value for content.
        tag (str): Value for tag.

    Returns:
        list[dict[str, Any]]: Dictionary containing computed output values.
    """
    errors: list[dict[str, Any]] = []
    pos = 0

    while True:
        start = content.find(f"<{tag}", pos)
        if start == -1:
            break

        gt = content.find(">", start)
        lt = content.find("<", start + 1)

        if gt == -1 or (lt != -1 and lt < gt):
            line = content[:start].count("\n") + 1
            errors.append(
                {
                    "message": f"Unclosed <{tag}> tag (missing '>')",
                    "line": line,
                    "column": 1,
                    "level": 3,
                    "domain": "heuristic",
                }
            )
            break

        pos = gt + 1

    return errors


@typechecked
def find_obvious_html_breaks(content: str) -> list[dict[str, Any]]:
    """Find obvious html breaks within the input data.

    Args:
        content (str): Value for content.

    Returns:
        list[dict[str, Any]]: Dictionary containing computed output values.
    """
    errors: list[dict[str, Any]] = []

    html_pos = content.find("<html")
    if html_pos != -1:
        gt = content.find(">", html_pos)
        lt = content.find("<", html_pos + 1)
        if gt == -1 or (lt != -1 and lt < gt):
            errors.append(
                {
                    "message": "Unclosed <html> tag (missing '>')",
                    "line": content[:html_pos].count("\n") + 1,
                    "column": 1,
                    "level": 3,
                    "domain": "heuristic",
                }
            )

    for tag in VOID_TAGS:
        errors.extend(find_unclosed_void_tags(content, tag))
    return errors


@typechecked
def validate_css_properties(css: str) -> list[dict[str, Any]]:
    """Validate css properties against expected rules.

    Args:
        css (str): Value for css.

    Returns:
        list[dict[str, Any]]: Dictionary containing computed output values.
    """
    errors: list[dict[str, Any]] = []
    typos = {
        "colour": "color",
        "margn": "margin",
        "wdith": "width",
        "heigt": "height",
    }

    for typo, correct in typos.items():
        if re.search(rf"\b{typo}\s*:", css):
            errors.append({"message": f"Did you mean '{correct}' instead of '{typo}'?", "level": 1})
    return errors


@typechecked
def validate_css_basic(content: str) -> list[dict[str, Any]]:
    """Validate css basic against expected rules.

    Args:
        content (str): Value for content.

    Returns:
        list[dict[str, Any]]: Dictionary containing computed output values.
    """
    errors: list[dict[str, Any]] = []
    style_blocks = re.findall(r"<style[^>]*>(.*?)</style>", content, re.S | re.I)

    for index, css in enumerate(style_blocks, start=1):
        if css.count("{") != css.count("}"):
            errors.append(
                {
                    "message": f"CSS error in <style> block #{index}: mismatched {{ }}",
                    "raw": None,
                    "line": None,
                    "column": None,
                }
            )
        errors.extend(validate_css_properties(css))
    return errors


@typechecked
def validate_html_structure(content: str) -> list[dict[str, Any]]:
    """Validate html structure against expected rules.

    Args:
        content (str): Value for content.

    Returns:
        list[dict[str, Any]]: Dictionary containing computed output values.
    """
    errors: list[dict[str, Any]] = []
    seen: set[tuple[Any, Any, Any]] = set()

    heuristic_errors = find_obvious_html_breaks(content)
    errors.extend(heuristic_errors)
    if any(int(error.get("level", 0)) >= 3 for error in heuristic_errors):
        return errors

    try:
        content = fix_common_entities(content)
        parser = html.HTMLParser(recover=True, remove_comments=False)
        _ = html.fromstring(content, parser=parser)

        for err in parser.error_log:
            if err.level < 0:
                continue

            key = (err.message, err.line, err.column)
            if key in seen:
                continue
            seen.add(key)

            normalized = normalize_lxml_error(err.message)
            if normalized["line"] is None and err.line is not None:
                normalized["line"] = err.line
            if normalized["column"] is None and err.column is not None:
                normalized["column"] = err.column

            errors.append({**normalized, "level": err.level, "domain": err.domain_name})

    except ParserError as exc:
        errors.append(
            {
                "message": "Fatal HTML parsing error",
                "raw": str(exc),
                "line": None,
                "column": None,
                "level": 4,
                "domain": "parser",
            }
        )

    return errors
