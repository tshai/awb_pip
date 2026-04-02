import json
from urllib.parse import urlparse

from typeguard import typechecked  # type: ignore


@typechecked
def href_points_to_page(href: str, file_name: str) -> bool:
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
    normalized_scope = str(remove_from or "").strip().lower()
    if normalized_scope not in {"header", "footer", "both"}:
        raise ValueError("remove_from must be one of: header, footer, both.")
    return normalized_scope


@typechecked
def normalize_let_ai_chat_reply(helper_reply: object, ai_id: str) -> tuple[str, bool]:
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
