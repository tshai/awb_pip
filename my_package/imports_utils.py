import json
import uuid

from bs4 import BeautifulSoup
from typeguard import typechecked  # type: ignore


@typechecked
def map_model_type(model_id: str) -> str:
    """Map model type to the expected target value.

    Args:
        model_id (str): Identifier for model.

    Returns:
        str: String result produced by this function.
    """
    model_mapping = {
        "1": "Qwen/Qwen3-30B-A3B-Thinking-2507",
        "2": "Qwen/Qwen3-235B-A22B-Thinking-2507",
        "3": "openai/gpt-oss-120b",
        "4": "NousResearch/Hermes-4-70B",
        "5": "gpt-4o-mini",
        "6": "Qwen/Qwen3-30B-A3B-Instruct-2507",
        "7": "gemini-2.5-flash",
        "8": "gemini-3-flash-preview",
    }
    return model_mapping.get(str(model_id), "openai/gpt-oss-20b")


@typechecked
def add_ai_ids_to_html_string_new(html: str) -> str:
    """Compute add ai ids to html string new for this workflow.

    Args:
        html (str): HTML content or fragment to process.

    Returns:
        str: String result produced by this function.
    """
    soup = BeautifulSoup(html, "html.parser")

    skip_tags = {"script", "style", "meta", "title", "link"}
    section_counter = 0
    current_section_id = None
    section_tag_counters: dict[str, int] = {}

    for element in soup.find_all(True):
        tag_name = element.name
        if tag_name in skip_tags:
            continue
        if element.has_attr("data-ai-id"):
            continue

        if tag_name == "section":
            section_counter += 1
            current_section_id = f"s{section_counter}"
            section_tag_counters = {}
            element["data-ai-id"] = current_section_id
            continue

        if current_section_id:
            section_tag_counters[tag_name] = section_tag_counters.get(tag_name, 0) + 1
            element["data-ai-id"] = f"{current_section_id}-{tag_name}{section_tag_counters[tag_name]}"
        else:
            section_tag_counters[tag_name] = section_tag_counters.get(tag_name, 0) + 1
            element["data-ai-id"] = f"{tag_name}{section_tag_counters[tag_name]}"

    return str(soup)


@typechecked
def add_ai_ids_to_html_string(html: str) -> str:
    """Compute add ai ids to html string for this workflow.

    Args:
        html (str): HTML content or fragment to process.

    Returns:
        str: String result produced by this function.
    """
    soup = BeautifulSoup(html, "html.parser")
    skip_tags = {"script", "style", "meta", "title", "link"}
    counters: dict[str, int] = {}

    for element in soup.find_all(True):
        tag_name = element.name
        if tag_name in skip_tags:
            continue
        if element.has_attr("data-ai-id"):
            continue

        counters[tag_name] = counters.get(tag_name, 0) + 1
        ai_id = f"{tag_name}-{uuid.uuid4().hex[:6]}-{counters[tag_name]}"
        element["data-ai-id"] = ai_id

    return str(soup)


@typechecked
def filter_messages(messages_history: list[dict], include_deleted: bool = False) -> list[dict]:
    """Compute filter messages for this workflow.

    Args:
        messages_history (list[dict]): Value for messages history.
        include_deleted (bool): Boolean flag for include deleted.

    Returns:
        list[dict]: Dictionary containing computed output values.
    """
    filtered_messages: list[dict] = []

    for message in messages_history:
        if not isinstance(message, dict):
            continue
        try:
            is_deleted = int(message.get("is_delete", 0) or 0) == 1
        except (TypeError, ValueError):
            is_deleted = str(message.get("is_delete", "")).strip().lower() in {"1", "true", "yes"}
        if is_deleted and not include_deleted:
            continue

        sender_type_raw = message.get("sender_type")
        try:
            sender_type = int(sender_type_raw)
        except (TypeError, ValueError):
            sender_type = sender_type_raw

        raw_text = message.get("message_text") or ""
        text = str(raw_text).strip()
        if sender_type == 0 and text.startswith("{") and text.endswith("}"):
            try:
                parsed = json.loads(text)
                if isinstance(parsed, dict) and "message" in parsed:
                    text = str(parsed["message"] or "").strip()
            except Exception:
                pass

        filtered_messages.append(
            {
                "id": message.get("id"),
                "conversation_id": message.get("conversation_id"),
                "page_id": message.get("page_id"),
                "sender_type": sender_type,
                "message_text": text,
            }
        )

    return filtered_messages
