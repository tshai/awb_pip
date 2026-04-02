from __future__ import annotations

import json
import os
from typing import Any

from typeguard import typechecked  # type: ignore

GOOGLE_SCHEMA_DROP_KEYS: set[str] = {
    "$schema",
    "$id",
    "$defs",
    "definitions",
    "title",
    "default",
    "examples",
    "example",
    "additionalProperties",
    "patternProperties",
    "discriminator",
    "readOnly",
    "writeOnly",
    "deprecated",
    "const",
    "if",
    "then",
    "else",
    "not",
    "contains",
    "prefixItems",
    "unevaluatedProperties",
    "unevaluatedItems",
    "minContains",
    "maxContains",
    "contentEncoding",
    "contentMediaType",
    "contentSchema",
}

GOOGLE_SCHEMA_ALLOWED_KEYS: set[str] = {
    "type",
    "format",
    "description",
    "nullable",
    "enum",
    "items",
    "properties",
    "required",
}


@typechecked
def decode_json_pointer_token(token: str) -> str:
    """Decode json pointer token into a usable value.

    Args:
        token (str): Value for token.

    Returns:
        str: String result produced by this function.
    """
    return str(token).replace("~1", "/").replace("~0", "~")


@typechecked
def resolve_local_schema_ref(root_schema: dict[str, Any], ref_value: str) -> dict[str, Any]:
    """Resolve local schema ref using available context.

    Args:
        root_schema (dict[str, Any]): Value for root schema.
        ref_value (str): Value for ref value.

    Returns:
        dict[str, Any]: Dictionary containing computed output values.
    """
    normalized_ref = str(ref_value or "").strip()
    if not normalized_ref.startswith("#/"):
        raise ValueError(f"Only local schema refs are supported. Got ref='{normalized_ref}'.")

    current_node: Any = root_schema
    for raw_token in normalized_ref[2:].split("/"):
        token = decode_json_pointer_token(raw_token)
        if not isinstance(current_node, dict) or token not in current_node:
            raise ValueError(f"Could not resolve schema ref '{normalized_ref}'.")
        current_node = current_node[token]

    if not isinstance(current_node, dict):
        raise ValueError(f"Schema ref '{normalized_ref}' must resolve to an object.")
    return current_node


@typechecked
def sanitize_google_schema_for_cache(schema_node: object, root_schema: dict[str, Any]) -> object:
    """Sanitize google schema for cache for safe downstream use.

    Args:
        schema_node (object): Value for schema node.
        root_schema (dict[str, Any]): Value for root schema.

    Returns:
        object: Computed result from this function.
    """
    if isinstance(schema_node, dict):
        working_node: dict[str, Any] = dict(schema_node)
        ref_value = working_node.get("$ref")
        if ref_value is not None:
            resolved_ref_node = resolve_local_schema_ref(root_schema, str(ref_value))
            merged_node: dict[str, Any] = dict(resolved_ref_node)
            for key, value in working_node.items():
                if key == "$ref":
                    continue
                merged_node[key] = value
            working_node = merged_node

        sanitized_obj: dict[str, Any] = {}
        for key, value in working_node.items():
            normalized_key = str(key or "").strip()
            if not normalized_key:
                continue
            if normalized_key in GOOGLE_SCHEMA_DROP_KEYS:
                continue
            if normalized_key not in GOOGLE_SCHEMA_ALLOWED_KEYS:
                continue
            if normalized_key.startswith("$"):
                continue

            sanitized_value = sanitize_google_schema_for_cache(value, root_schema)
            if sanitized_value is None:
                continue

            if normalized_key == "properties":
                if not isinstance(value, dict):
                    raise ValueError("Schema 'properties' must be an object.")
                sanitized_properties: dict[str, object] = {}
                for prop_name, prop_schema in value.items():
                    normalized_prop_name = str(prop_name or "").strip()
                    if not normalized_prop_name:
                        continue
                    sanitized_prop_schema = sanitize_google_schema_for_cache(prop_schema, root_schema)
                    if sanitized_prop_schema is None:
                        continue
                    sanitized_properties[normalized_prop_name] = sanitized_prop_schema
                sanitized_value = sanitized_properties

            if normalized_key == "type" and isinstance(sanitized_value, str):
                normalized_type = str(sanitized_value).strip().lower()
                if normalized_type == "object":
                    sanitized_value = "OBJECT"
                elif normalized_type == "string":
                    sanitized_value = "STRING"
                elif normalized_type == "integer":
                    sanitized_value = "INTEGER"
                elif normalized_type == "number":
                    sanitized_value = "NUMBER"
                elif normalized_type == "boolean":
                    sanitized_value = "BOOLEAN"
                elif normalized_type == "array":
                    sanitized_value = "ARRAY"
                else:
                    sanitized_value = str(sanitized_value).strip().upper()

            sanitized_obj[normalized_key] = sanitized_value

        return sanitized_obj

    if isinstance(schema_node, list):
        sanitized_list: list[object] = []
        for item in schema_node:
            sanitized_item = sanitize_google_schema_for_cache(item, root_schema)
            if sanitized_item is None:
                continue
            sanitized_list.append(sanitized_item)
        return sanitized_list

    return schema_node


@typechecked
def extract_tool_schema_for_cache(tool: object) -> dict[str, Any]:
    """Extract tool schema for cache from the provided data.

    Args:
        tool (object): Value for tool.

    Returns:
        dict[str, Any]: Dictionary containing computed output values.
    """
    args_schema = getattr(tool, "args_schema", None)
    if args_schema is None:
        return {"type": "object", "properties": {}}

    model_json_schema_fn = getattr(args_schema, "model_json_schema", None)
    if callable(model_json_schema_fn):
        schema_value = model_json_schema_fn()
        if not isinstance(schema_value, dict):
            raise ValueError("Tool args schema must return a JSON object.")
        sanitized_schema = sanitize_google_schema_for_cache(schema_value, schema_value)
        if not isinstance(sanitized_schema, dict):
            raise ValueError("Sanitized tool args schema must be a JSON object.")
        if str(sanitized_schema.get("type") or "").strip().lower() == "object":
            sanitized_schema.setdefault("properties", {})
        return sanitized_schema

    schema_fn = getattr(args_schema, "schema", None)
    if callable(schema_fn):
        schema_value = schema_fn()
        if not isinstance(schema_value, dict):
            raise ValueError("Tool args schema must return a JSON object.")
        sanitized_schema = sanitize_google_schema_for_cache(schema_value, schema_value)
        if not isinstance(sanitized_schema, dict):
            raise ValueError("Sanitized tool args schema must be a JSON object.")
        if str(sanitized_schema.get("type") or "").strip().lower() == "object":
            sanitized_schema.setdefault("properties", {})
        return sanitized_schema

    raise ValueError("Tool args_schema must expose schema() or model_json_schema().")


@typechecked
def build_google_cache_tools_payload(tools_site: object) -> list[dict[str, Any]]:
    """Build google cache tools payload from the provided inputs.

    Args:
        tools_site (object): Value for tools site.

    Returns:
        list[dict[str, Any]]: Dictionary containing computed output values.
    """
    if not isinstance(tools_site, (list, tuple)):
        raise ValueError("tools_site must be a list or tuple of tools.")

    declarations: list[dict[str, Any]] = []
    seen_names: set[str] = set()
    for tool in tools_site:
        tool_name = str(getattr(tool, "name", "")).strip()
        if not tool_name:
            raise ValueError("Each tool in tools_site must include a non-empty name.")
        if tool_name in seen_names:
            continue
        seen_names.add(tool_name)
        declarations.append(
            {
                "name": tool_name,
                "description": str(getattr(tool, "description", "")).strip(),
                "parameters": extract_tool_schema_for_cache(tool),
            }
        )

    if not declarations:
        return []
    return [{"function_declarations": declarations}]


@typechecked
def build_tools_list_json_for_db(tools_site: object) -> str:
    """Build tools list json for db from the provided inputs.

    Args:
        tools_site (object): Value for tools site.

    Returns:
        str: String result produced by this function.
    """
    if not isinstance(tools_site, (list, tuple)):
        raise ValueError("tools_site must be a list or tuple of tools.")

    tool_names: list[str] = []
    seen: set[str] = set()
    for tool in tools_site:
        tool_name = str(getattr(tool, "name", "")).strip()
        if not tool_name:
            raise ValueError("Each tool in tools_site must include a non-empty name.")
        if tool_name in seen:
            continue
        seen.add(tool_name)
        tool_names.append(tool_name)

    return json.dumps(tool_names, ensure_ascii=False)


@typechecked
def load_google_generativeai():
    """Load google generativeai from the configured source.

    Returns:
        Any: Computed result from this function.
    """
    try:
        from google import genai as genai_module  # type: ignore
        return genai_module
    except Exception:
        return None


@typechecked
def resolve_google_api_keys_for_cache() -> list[str]:
    """Resolve google api keys for cache using available context.

    Returns:
        list[str]: List containing computed output items.
    """
    keys: list[str] = []
    seen: set[str] = set()

    gemini_api_key = str(os.getenv("GEMINI_API_KEY") or "").strip()
    if gemini_api_key and gemini_api_key not in seen:
        keys.append(gemini_api_key)
        seen.add(gemini_api_key)

    google_api_key = str(os.getenv("GOOGLE_API_KEY") or "").strip()
    if google_api_key and google_api_key not in seen:
        keys.append(google_api_key)
        seen.add(google_api_key)

    if not keys:
        raise ValueError("Missing GEMINI_API_KEY or GOOGLE_API_KEY for Gemini cache generation.")

    return keys


@typechecked
def resolve_google_api_key_for_cache() -> str:
    """Resolve google api key for cache using available context.

    Returns:
        str: String result produced by this function.
    """
    return resolve_google_api_keys_for_cache()[0]


@typechecked
def configure_google_generativeai_for_cache(genai_module: object) -> None:
    """Compute configure google generativeai for cache for this workflow.

    Args:
        genai_module (object): Value for genai module.

    Returns:
        None: This function does not return a value.
    """
    client_cls = getattr(genai_module, "Client", None)
    if client_cls is None:
        raise RuntimeError("google.genai.Client is unavailable.")
    resolve_google_api_key_for_cache()


@typechecked
def build_google_genai_client(genai_module: object) -> Any:
    """Build google genai client from the provided inputs.

    Args:
        genai_module (object): Value for genai module.

    Returns:
        Any: Computed result from this function.
    """
    api_key = resolve_google_api_key_for_cache()
    return build_google_genai_client_with_api_key(genai_module, api_key)


@typechecked
def build_google_genai_client_with_api_key(genai_module: object, api_key: str) -> Any:
    """Build google genai client with api key from the provided inputs.

    Args:
        genai_module (object): Value for genai module.
        api_key (str): Value for api key.

    Returns:
        Any: Computed result from this function.
    """
    client_cls = getattr(genai_module, "Client", None)
    if client_cls is None:
        raise RuntimeError("google.genai.Client is unavailable.")
    normalized_api_key = str(api_key or "").strip()
    if not normalized_api_key:
        raise ValueError("api_key is required.")
    return client_cls(api_key=normalized_api_key)


@typechecked
def is_cache_not_found_error(exc: Exception) -> bool:
    """Return whether cache not found error is true for the given input.

    Args:
        exc (Exception): Value for exc.

    Returns:
        bool: True when the condition is met; otherwise False.
    """
    class_name = str(exc.__class__.__name__ or "").lower()
    message = str(exc or "").lower()
    if "notfound" in class_name:
        return True
    if "404" in message:
        return True
    if "not found" in message:
        return True
    return False


@typechecked
def is_google_api_key_invalid_error(exc: Exception) -> bool:
    """Return whether google api key invalid error is true for the given input.

    Args:
        exc (Exception): Value for exc.

    Returns:
        bool: True when the condition is met; otherwise False.
    """
    message = str(exc or "").lower()
    return (
        "api_key_invalid" in message
        or "api key expired" in message
        or "invalid api key" in message
    )


@typechecked
def call_google_cached_content_get(cached_content_api: object, cache_id: str) -> Any:
    """Compute call google cached content get for this workflow.

    Args:
        cached_content_api (object): Value for cached content api.
        cache_id (str): Identifier for cache.

    Returns:
        Any: Computed result from this function.
    """
    get_fn = getattr(cached_content_api, "get", None)
    if not callable(get_fn):
        raise RuntimeError("google.genai client.caches.get API is unavailable.")
    return get_fn(name=cache_id)


@typechecked
def call_google_cached_content_delete(cached_content_api: object, cache_id: str) -> None:
    """Compute call google cached content delete for this workflow.

    Args:
        cached_content_api (object): Value for cached content api.
        cache_id (str): Identifier for cache.

    Returns:
        None: This function does not return a value.
    """
    delete_fn = getattr(cached_content_api, "delete", None)
    if not callable(delete_fn):
        raise RuntimeError("google.genai client.caches.delete API is unavailable.")
    delete_fn(name=cache_id)
