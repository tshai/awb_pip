import hashlib
import json
import re

from typeguard import typechecked  # type: ignore


@typechecked
def parse_codegen_tables(raw_tables: str) -> str:
    """Parse codegen tables into a structured Python value.

    Args:
        raw_tables (str): Raw input value for tables.

    Returns:
        str: String result produced by this function.
    """
    text = str(raw_tables or "").strip()
    if not text:
        return ""

    tokens = [item.strip() for item in text.split(",") if item.strip()]
    if not tokens:
        return ""

    invalid = [token for token in tokens if not re.fullmatch(r"[A-Za-z0-9_]+", token)]
    if invalid:
        raise ValueError(f"Invalid table names: {', '.join(invalid)}")

    seen: set[str] = set()
    normalized: list[str] = []
    for token in tokens:
        if token not in seen:
            seen.add(token)
            normalized.append(token)
    return ",".join(normalized)


@typechecked
def validate_full_qa_positive_int(raw_value: str, field_name: str) -> int:
    """Validate full qa positive int against expected rules.

    Args:
        raw_value (str): Raw input value for value.
        field_name (str): Value for field name.

    Returns:
        int: Integer result produced by this function.
    """
    try:
        parsed = int(str(raw_value).strip())
    except (TypeError, ValueError):
        raise ValueError(f"{field_name} must be a positive integer.")
    if parsed <= 0:
        raise ValueError(f"{field_name} must be a positive integer.")
    return parsed


@typechecked
def validate_full_qa_run_llm(raw_value: str) -> str:
    """Validate full qa run llm against expected rules.

    Args:
        raw_value (str): Raw input value for value.

    Returns:
        str: String result produced by this function.
    """
    normalized = str(raw_value).strip().lower()
    if normalized not in {"true", "false"}:
        raise ValueError("Run LLM must be true or false.")
    return normalized


@typechecked
def validate_full_qa_start_url(raw_value: str) -> str:
    """Validate full qa start url against expected rules.

    Args:
        raw_value (str): Raw input value for value.

    Returns:
        str: String result produced by this function.
    """
    normalized = str(raw_value).strip()
    if not normalized:
        raise ValueError("Start URL is required.")
    if not (normalized.startswith("http://") or normalized.startswith("https://")):
        raise ValueError("Start URL must start with http:// or https://.")
    return normalized


@typechecked
def normalize_gemini_admin_model(raw_model: str) -> str:
    """Normalize gemini admin model into a consistent format.

    Args:
        raw_model (str): Raw input value for model.

    Returns:
        str: String result produced by this function.
    """
    normalized_model = str(raw_model).strip()
    allowed_models = {"gemini-2.5-flash", "gemini-3-flash-preview"}
    if normalized_model not in allowed_models:
        raise ValueError("Invalid Gemini model selection.")
    return normalized_model


@typechecked
def normalize_admin_tools_json_input(tools_json_input: str) -> str:
    """Normalize admin tools json input into a consistent format.

    Args:
        tools_json_input (str): JSON text/value used by this function.

    Returns:
        str: String result produced by this function.
    """
    normalized_tools_json_input = str(tools_json_input).strip()
    if not normalized_tools_json_input:
        raise ValueError("tools_json is required.")

    try:
        parsed_tools = json.loads(normalized_tools_json_input)
    except json.JSONDecodeError as exc:
        raise ValueError("tools_json must be valid JSON.") from exc

    if not isinstance(parsed_tools, list):
        raise ValueError("tools_json must be a JSON array.")

    return json.dumps(parsed_tools, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


@typechecked
def validate_admin_expire_time_hours_input(expire_time_hours_input: str) -> int:
    """Validate admin expire time hours input against expected rules.

    Args:
        expire_time_hours_input (str): Value for expire time hours input.

    Returns:
        int: Integer result produced by this function.
    """
    normalized_value = str(expire_time_hours_input).strip()
    if not normalized_value:
        raise ValueError("expire_time_hours is required.")
    try:
        parsed_value = int(normalized_value)
    except ValueError as exc:
        raise ValueError("expire_time_hours must be an integer.") from exc
    if parsed_value <= 0:
        raise ValueError("expire_time_hours must be a positive integer.")
    return parsed_value


@typechecked
def build_admin_cache_identifier(
    resolved_model_name: str,
    llm_model_name_input: str,
    system_promte_input: str,
    user_message_input: str,
    tools_json_input: str,
) -> str:
    """Build admin cache identifier from the provided inputs.

    Args:
        resolved_model_name (str): Value for resolved model name.
        llm_model_name_input (str): Value for llm model name input.
        system_promte_input (str): Value for system promte input.
        user_message_input (str): Value for user message input.
        tools_json_input (str): JSON text/value used by this function.

    Returns:
        str: String result produced by this function.
    """
    normalized_model = str(resolved_model_name).strip()
    if not normalized_model:
        raise ValueError("Resolved model name is required.")

    normalized_llm_model_name = str(llm_model_name_input).strip()
    normalized_system_promte = str(system_promte_input).strip()
    _normalized_user_message = str(user_message_input).strip()
    normalized_tools_json = normalize_admin_tools_json_input(tools_json_input)

    if not normalized_llm_model_name:
        raise ValueError("llm_model_name is required.")
    if len(normalized_llm_model_name) > 255:
        raise ValueError("llm_model_name must be 255 characters or less.")
    if not normalized_system_promte:
        raise ValueError("system_promte is required.")

    safe_model = re.sub(r"[^A-Za-z0-9_-]+", "_", normalized_model)
    safe_selected_model = re.sub(r"[^A-Za-z0-9_-]+", "_", normalized_llm_model_name)
    fingerprint_source = f"{normalized_system_promte}\n---\n{normalized_tools_json}"
    fingerprint = hashlib.sha1(fingerprint_source.encode("utf-8")).hexdigest()[:16]
    identifier = f"admin_cache_{safe_model}_{safe_selected_model}_{fingerprint}"
    if len(identifier) > 255:
        raise ValueError("Generated cache message_name exceeds 255 characters.")
    return identifier
