import hashlib
import hmac
import json
import os
import re

from typeguard import typechecked  # type: ignore


@typechecked
def internal_proxy_token() -> str:
    """Compute internal proxy token for this workflow.

    Returns:
        str: String result produced by this function.
    """
    explicit_token = str(os.getenv("INTERNAL_LLM_PROXY_TOKEN") or "").strip()
    if explicit_token:
        return explicit_token

    secret_key = str(os.getenv("FLASK_SECRET_KEY") or "").strip()
    if not secret_key:
        return ""

    return hmac.new(secret_key.encode("utf-8"), b"llm_proxy_internal", hashlib.sha256).hexdigest()


@typechecked
def extract_tool_schema_for_cache(tool: object) -> dict:
    """Extract tool schema for cache from the provided data.

    Args:
        tool (object): Value for tool.

    Returns:
        dict: Dictionary containing computed output values.
    """
    args_schema = getattr(tool, "args_schema", None)
    if args_schema is None:
        return {"type": "object", "properties": {}}

    model_json_schema_fn = getattr(args_schema, "model_json_schema", None)
    if callable(model_json_schema_fn):
        schema_value = model_json_schema_fn()
        if not isinstance(schema_value, dict):
            raise ValueError("Tool args schema must return a JSON object.")
        return schema_value

    schema_fn = getattr(args_schema, "schema", None)
    if callable(schema_fn):
        schema_value = schema_fn()
        if not isinstance(schema_value, dict):
            raise ValueError("Tool args schema must return a JSON object.")
        return schema_value

    raise ValueError("Tool args_schema must expose schema() or model_json_schema().")


@typechecked
def build_cache_tools_json(tools_site: object) -> str:
    """Build cache tools json from the provided inputs.

    Args:
        tools_site (object): Value for tools site.

    Returns:
        str: String result produced by this function.
    """
    if not isinstance(tools_site, (list, tuple)):
        raise ValueError("tools_site must be a list or tuple of tools.")

    tools_by_name: dict[str, object] = {}
    for tool in tools_site:
        tool_name = str(getattr(tool, "name", "")).strip()
        if not tool_name:
            raise ValueError("Each tool in tools_site must include a non-empty name.")
        if tool_name in tools_by_name:
            continue
        tools_by_name[tool_name] = tool

    normalized_payload: list[dict] = []
    for tool_name in sorted(tools_by_name.keys()):
        tool = tools_by_name[tool_name]
        normalized_payload.append(
            {
                "name": tool_name,
                "description": str(getattr(tool, "description", "")).strip(),
                "parameters": extract_tool_schema_for_cache(tool),
            }
        )

    return json.dumps(normalized_payload, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


@typechecked
def strip_system_messages_for_cached_content(messages_site: object) -> list[object]:
    """Strip system messages for cached content from the given value.

    Args:
        messages_site (object): Value for messages site.

    Returns:
        list[object]: List containing computed output items.
    """
    if not isinstance(messages_site, (list, tuple)):
        raise ValueError("messages_site must be a list or tuple.")

    filtered_messages: list[object] = []
    for message in messages_site:
        if isinstance(message, dict):
            role_value = str(message.get("role") or message.get("type") or "").strip().lower()
            if role_value == "system":
                continue
            filtered_messages.append(message)
            continue

        message_type_value = str(getattr(message, "type", "") or "").strip().lower()
        message_class_name = str(getattr(message, "__class__", type(message)).__name__).strip()
        if message_class_name == "SystemMessage" or message_type_value == "system":
            continue
        filtered_messages.append(message)

    if not filtered_messages:
        raise ValueError("messages_site must include at least one non-system message when using cache_id.")

    for message in filtered_messages:
        if isinstance(message, dict):
            role_value = str(message.get("role") or message.get("type") or "").strip().lower()
            if role_value == "system":
                raise ValueError("System messages are not allowed when using cache_id.")
            continue

        message_type_value = str(getattr(message, "type", "") or "").strip().lower()
        if message_type_value == "system":
            raise ValueError("System messages are not allowed when using cache_id.")

    return filtered_messages


@typechecked
def build_gemini_cache_key_and_instructions(system_promte: object, resolved_model: str, tools_site: object) -> tuple[str, str]:
    """Build gemini cache key and instructions from the provided inputs.

    Args:
        system_promte (object): Value for system promte.
        resolved_model (str): Value for resolved model.
        tools_site (object): Value for tools site.

    Returns:
        tuple[str, str]: Tuple containing computed output values.
    """
    normalized_model = str(resolved_model).strip()
    normalized_system_promte = str(system_promte).strip()
    if not normalized_model:
        raise ValueError("resolved model name is required.")
    if not normalized_system_promte:
        raise ValueError("system_promte is required.")

    tools_json = build_cache_tools_json(tools_site)
    fingerprint_source = f"{normalized_system_promte}\n---\n{tools_json}"
    fingerprint = hashlib.sha1(fingerprint_source.encode("utf-8")).hexdigest()[:16]
    safe_model = re.sub(r"[^A-Za-z0-9_-]+", "_", normalized_model)
    message_identifier = f"admin_cache_{safe_model}_{safe_model}_{fingerprint}"
    if len(message_identifier) > 255:
        raise ValueError("Generated cache message_name exceeds 255 characters.")

    cache_instructions = "SYSTEM_PROMTE:\n" f"{normalized_system_promte}\n\n" "TOOLS_JSON:\n" f"{tools_json}"
    return message_identifier, cache_instructions


@typechecked
def is_cache_id_input(raw_value: str) -> bool:
    """Return whether cache id input is true for the given input.

    Args:
        raw_value (str): Raw input value for value.

    Returns:
        bool: True when the condition is met; otherwise False.
    """
    normalized = str(raw_value or "").strip()
    return normalized.lower().startswith("cachedcontents/")


@typechecked
def parse_tool_names_from_cache_row(tools_list_raw: object) -> list[str]:
    """Parse tool names from cache row into a structured Python value.

    Args:
        tools_list_raw (object): Value for tools list raw.

    Returns:
        list[str]: List containing computed output items.
    """
    normalized_raw = str(tools_list_raw or "").strip()
    if not normalized_raw:
        raise ValueError("tools_list is required in llm_cache_id to recreate cache.")

    try:
        parsed_value = json.loads(normalized_raw)
    except json.JSONDecodeError as exc:
        raise ValueError("tools_list in llm_cache_id must be a valid JSON array.") from exc

    if not isinstance(parsed_value, list):
        raise ValueError("tools_list in llm_cache_id must be a JSON array.")

    normalized_names: list[str] = []
    seen: set[str] = set()
    for item in parsed_value:
        tool_name = str(item or "").strip()
        if not tool_name:
            continue
        if tool_name in seen:
            continue
        seen.add(tool_name)
        normalized_names.append(tool_name)

    if not normalized_names:
        raise ValueError("tools_list in llm_cache_id must contain at least one tool name.")
    return normalized_names
