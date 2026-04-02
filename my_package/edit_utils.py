import json
from urllib.parse import urlparse

from typeguard import typechecked  # type: ignore


@typechecked
def tag_has_ai_id(tag: object) -> bool:
    """Compute tag has ai id for this workflow.

    Args:
        tag (object): Value for tag.

    Returns:
        bool: True when the condition is met; otherwise False.
    """
    if tag is None:
        return False
    attrs_value = getattr(tag, "attrs", None)
    if not isinstance(attrs_value, dict):
        return False
    return bool(str(attrs_value.get("data-ai-id") or "").strip())


@typechecked
def href_points_to_page(href: str, file_name: str) -> bool:
    """Compute href points to page for this workflow.

    Args:
        href (str): URL or link value used by this function.
        file_name (str): File-system path or file name used by this function.

    Returns:
        bool: True when the condition is met; otherwise False.
    """
    raw_href = str(href or "").strip()
    if not raw_href:
        return False

    lower_href = raw_href.lower()
    if (
        lower_href.startswith("javascript:")
        or lower_href.startswith("mailto:")
        or lower_href.startswith("tel:")
        or lower_href.startswith("#")
    ):
        return False

    parsed = urlparse(raw_href)
    path = (parsed.path or raw_href).replace("\\", "/").strip().lower()
    while path.startswith("./"):
        path = path[2:]
    path = path.lstrip("/")
    if path.endswith("/"):
        path = path[:-1]

    target = str(file_name or "").strip().lower()
    if not target:
        return False
    target_stem = target[:-5] if target.endswith(".html") else target

    if path == target or path == target_stem:
        return True
    if path.endswith("/" + target) or path.endswith("/" + target_stem):
        return True
    return False


@typechecked
def normalize_link_cleanup_scope(remove_from: str) -> str:
    """Normalize link cleanup scope into a consistent format.

    Args:
        remove_from (str): Value for remove from.

    Returns:
        str: String result produced by this function.
    """
    normalized_scope = str(remove_from or "").strip().lower()
    if normalized_scope not in {"header", "footer", "both"}:
        raise ValueError("remove_from must be one of: header, footer, both.")
    return normalized_scope


@typechecked
def normalize_let_ai_chat_reply(helper_reply: object, ai_id: str) -> tuple[str, bool]:
    """Normalize let ai chat reply into a consistent format.

    Args:
        helper_reply (object): Value for helper reply.
        ai_id (str): Identifier for ai.

    Returns:
        tuple[str, bool]: Tuple containing computed output values.
    """
    default_text = f'Completed. Block "{ai_id}" was updated.'
    reload_iframe = True

    if isinstance(helper_reply, dict):
        if "assistant_reply" in helper_reply or "reload_iframe" in helper_reply:
            message = str(helper_reply.get("assistant_reply", "")).strip() or default_text
            reload_iframe = bool(helper_reply.get("reload_iframe", True))
            if message.upper().startswith("QUESTION:") or message.upper().startswith("ERROR:"):
                reload_iframe = False
            return message, reload_iframe

        status = str(helper_reply.get("status", "")).strip().lower()
        text = str(helper_reply.get("text", "")).strip()
        if status == "working":
            reload_iframe = False
        elif status == "finish":
            reload_iframe = True
        message = text or default_text
        if message.upper().startswith("QUESTION:") or message.upper().startswith("ERROR:"):
            reload_iframe = False
        return message, reload_iframe

    raw = str(helper_reply).strip() if helper_reply is not None else ""
    if not raw:
        return default_text, True

    candidate = raw
    if candidate.startswith("```") and candidate.endswith("```"):
        lines = candidate.splitlines()
        if len(lines) >= 3:
            candidate = "\n".join(lines[1:-1]).strip()

    try:
        parsed = json.loads(candidate)
    except Exception:
        parsed = None

    if isinstance(parsed, dict):
        status = str(parsed.get("status", "")).strip().lower()
        text = str(parsed.get("text", "")).strip()
        if status == "working":
            reload_iframe = False
        elif status == "finish":
            reload_iframe = True
        message = text or raw
    elif isinstance(parsed, str) and parsed.strip():
        message = parsed.strip()
    else:
        message = raw

    if message.upper().startswith("ERROR:") or message.upper().startswith("QUESTION:"):
        reload_iframe = False
    return message, reload_iframe


@typechecked
def apply_source_file_attrs_to_ai_nodes(root_tag: object, source_file_name: str) -> None:
    """Compute apply source file attrs to ai nodes for this workflow.

    Args:
        root_tag (object): Value for root tag.
        source_file_name (str): File-system path or file name used by this function.

    Returns:
        None: This function does not return a value.
    """
    normalized_source = str(source_file_name or "").strip()
    if not normalized_source or root_tag is None:
        return

    ai_nodes: list[object] = []
    if tag_has_ai_id(root_tag):
        ai_nodes.append(root_tag)

    if hasattr(root_tag, "select"):
        selected_nodes = getattr(root_tag, "select")("[data-ai-id]")
        if isinstance(selected_nodes, list):
            for node in selected_nodes:
                if tag_has_ai_id(node):
                    ai_nodes.append(node)

    seen_nodes: set[int] = set()
    for node in ai_nodes:
        node_identity = id(node)
        if node_identity in seen_nodes:
            continue
        seen_nodes.add(node_identity)
        try:
            node["file_name"] = normalized_source  # type: ignore[index]
            node["data-awb-source-file"] = normalized_source  # type: ignore[index]
        except Exception:
            continue
