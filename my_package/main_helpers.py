import json
import os
import re
from datetime import date, datetime, timedelta
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from typing import Any
from urllib.parse import unquote, urlparse

from typeguard import typechecked  # type: ignore


@typechecked
def json_safe_value(value: Any) -> Any:
    """Compute json safe value for this workflow.

    Args:
        value (Any): Value for value.

    Returns:
        Any: Computed result from this function.
    """
    if isinstance(value, dict):
        cleaned: dict[Any, Any] = {}
        for key, item in value.items():
            if key == "_sa_instance_state":
                continue
            cleaned[key] = json_safe_value(item)
        return cleaned

    if isinstance(value, list):
        return [json_safe_value(item) for item in value]

    if isinstance(value, tuple):
        return [json_safe_value(item) for item in value]

    if isinstance(value, (str, int, float, bool)) or value is None:
        return value

    if isinstance(value, (datetime, date)):
        return value.isoformat()

    if isinstance(value, memoryview):
        return value.tobytes().hex()

    if isinstance(value, (bytes, bytearray)):
        return bytes(value).hex()

    to_dict = getattr(value, "to_dict", None)
    if callable(to_dict):
        try:
            return json_safe_value(to_dict())
        except Exception:
            pass

    return str(value)


@typechecked
def collect_gallery_image_urls(raw_urls: list[str], business_guid: str) -> list[str]:
    """Collect gallery image urls from available values.

    Args:
        raw_urls (list[str]): Raw input value for urls.
        business_guid (str): Unique identifier for business.

    Returns:
        list[str]: List containing computed output items.
    """
    allowed_prefix = f"/static/business/{business_guid}/images/"
    accepted: list[str] = []
    seen: set[str] = set()

    for raw_url in raw_urls:
        candidate = str(raw_url or "").strip()
        if not candidate:
            continue

        parsed = urlparse(candidate)
        normalized_path = unquote(parsed.path or "").replace("\\", "/")
        if ".." in normalized_path or not normalized_path.startswith(allowed_prefix):
            continue

        if parsed.scheme or parsed.netloc:
            sanitized = parsed._replace(query="", fragment="").geturl()
        else:
            sanitized = normalized_path

        if sanitized in seen:
            continue

        seen.add(sanitized)
        accepted.append(sanitized)

    return accepted


@typechecked
def merge_unique_urls(primary_urls: list[str], secondary_urls: list[str]) -> list[str]:
    """Merge unique urls into a single result.

    Args:
        primary_urls (list[str]): URL or link value used by this function.
        secondary_urls (list[str]): URL or link value used by this function.

    Returns:
        list[str]: List containing computed output items.
    """
    merged: list[str] = []
    seen: set[str] = set()
    for raw_url in [*primary_urls, *secondary_urls]:
        normalized = str(raw_url or "").strip()
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        merged.append(normalized)
    return merged


@typechecked
def normalize_trace_guid_for_logs(value: str, field_name: str) -> str:
    """Normalize trace guid for logs into a consistent format.

    Args:
        value (str): Value for value.
        field_name (str): Value for field name.

    Returns:
        str: String result produced by this function.
    """
    normalized_value = str(value or "").strip()
    if not normalized_value:
        raise ValueError(f"{field_name} is required.")
    if ".." in normalized_value or "/" in normalized_value or "\\" in normalized_value:
        raise ValueError(f"{field_name} contains invalid path characters.")
    return normalized_value


@typechecked
def extract_model_name_from_flow_summary(summary_text: str) -> str:
    """Extract model name from flow summary from the provided data.

    Args:
        summary_text (str): Value for summary text.

    Returns:
        str: String result produced by this function.
    """
    normalized_summary = str(summary_text or "").strip()
    if not normalized_summary:
        return ""

    model_match = re.search(r"(?:^|\\s)model=([^\\s]+)", normalized_summary)
    if model_match is None:
        return ""

    return str(model_match.group(1) or "").strip()


@typechecked
def parse_trace_timestamp(timestamp_text: str) -> tuple[bool, datetime]:
    """Parse trace timestamp into a structured Python value.

    Args:
        timestamp_text (str): Value for timestamp text.

    Returns:
        tuple[bool, datetime]: Tuple containing computed output values.
    """
    normalized_timestamp = str(timestamp_text or "").strip()
    if not normalized_timestamp:
        return False, datetime(1970, 1, 1)

    try:
        parsed_timestamp = datetime.strptime(normalized_timestamp, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return False, datetime(1970, 1, 1)

    return True, parsed_timestamp


@typechecked
def resolve_current_session_window(flow_events: list[dict[str, str]]) -> tuple[bool, datetime, datetime]:
    """Resolve current session window using available context.

    Args:
        flow_events (list[dict[str, str]]): Value for flow events.

    Returns:
        tuple[bool, datetime, datetime]: Tuple containing computed output values.
    """
    parsed_timestamps: list[datetime] = []
    for event in flow_events:
        is_valid_timestamp, event_timestamp = parse_trace_timestamp(str(event.get("timestamp") or ""))
        if is_valid_timestamp:
            parsed_timestamps.append(event_timestamp)

    if not parsed_timestamps:
        return False, datetime(1970, 1, 1), datetime(1970, 1, 1)

    sorted_timestamps = sorted(parsed_timestamps)
    max_gap_seconds = 600
    session_start = sorted_timestamps[0]
    session_end = sorted_timestamps[0]

    for event_timestamp in sorted_timestamps[1:]:
        gap_seconds = (event_timestamp - session_end).total_seconds()
        if gap_seconds > max_gap_seconds:
            session_start = event_timestamp
            session_end = event_timestamp
            continue
        session_end = event_timestamp

    tolerance = timedelta(seconds=20)
    return True, session_start - tolerance, session_end + tolerance


@typechecked
def parse_non_negative_int(value: Any) -> int:
    """Parse non negative int into a structured Python value.

    Args:
        value (Any): Value for value.

    Returns:
        int: Integer result produced by this function.
    """
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return max(value, 0)

    normalized_value = str(value or "").strip()
    if not normalized_value:
        return 0

    try:
        parsed = Decimal(normalized_value)
    except InvalidOperation:
        return 0

    if parsed < Decimal("0"):
        return 0

    return int(parsed)


@typechecked
def max_non_negative_int(values: list[Any]) -> int:
    """Compute max non negative int for this workflow.

    Args:
        values (list[Any]): Value for values.

    Returns:
        int: Integer result produced by this function.
    """
    max_value = 0
    for value in values:
        parsed_value = parse_non_negative_int(value)
        if parsed_value > max_value:
            max_value = parsed_value
    return max_value


@typechecked
def normalize_model_name_for_lookup(model_name: str) -> str:
    """Normalize model name for lookup into a consistent format.

    Args:
        model_name (str): Value for model name.

    Returns:
        str: String result produced by this function.
    """
    normalized_model_name = str(model_name or "").strip()
    if not normalized_model_name:
        return ""

    if normalized_model_name.startswith("models/"):
        normalized_model_name = normalized_model_name[len("models/"):]

    return normalized_model_name.strip()


@typechecked
def is_gemini_model_name(model_name: str) -> bool:
    """Return whether gemini model name is true for the given input.

    Args:
        model_name (str): Value for model name.

    Returns:
        bool: True when the condition is met; otherwise False.
    """
    normalized_model_name = normalize_model_name_for_lookup(model_name).lower()
    return "gemini" in normalized_model_name


@typechecked
def score_usage_candidate(raw_node: dict[str, Any]) -> tuple[int, int, int, int] | None:
    """Compute score usage candidate for this workflow.

    Args:
        raw_node (dict[str, Any]): Raw input value for node.

    Returns:
        tuple[int, int, int, int] | None: Tuple containing computed output values.
    """
    input_keys = [
        "input_tokens",
        "prompt_tokens",
        "promptTokenCount",
        "inputTokenCount",
    ]
    output_keys = [
        "output_tokens",
        "completion_tokens",
        "candidatesTokenCount",
        "outputTokenCount",
    ]
    cached_keys = [
        "cache_read_input_tokens",
        "cached_tokens",
        "cachedContentTokenCount",
        "cacheReadInputTokenCount",
        "cached_content_token_count",
    ]
    total_keys = [
        "total_tokens",
        "totalTokenCount",
    ]

    has_input = any(key in raw_node for key in input_keys)
    has_output = any(key in raw_node for key in output_keys)
    has_cached = any(key in raw_node for key in cached_keys)
    has_total = any(key in raw_node for key in total_keys)
    has_usage_shape = has_input or has_output or has_cached or has_total
    if not has_usage_shape:
        return None

    input_tokens = max_non_negative_int([raw_node.get(key) for key in input_keys if key in raw_node])
    output_tokens = max_non_negative_int([raw_node.get(key) for key in output_keys if key in raw_node])
    cached_tokens = max_non_negative_int([raw_node.get(key) for key in cached_keys if key in raw_node])
    total_tokens = max_non_negative_int([raw_node.get(key) for key in total_keys if key in raw_node])

    if input_tokens <= 0 and total_tokens > 0:
        derived_input_tokens = total_tokens - output_tokens
        if derived_input_tokens > 0:
            input_tokens = derived_input_tokens

    if input_tokens < cached_tokens and total_tokens > 0:
        derived_input_tokens = total_tokens - output_tokens
        if derived_input_tokens > input_tokens:
            input_tokens = derived_input_tokens

    if input_tokens < cached_tokens:
        input_tokens = cached_tokens

    score = 0
    if has_input:
        score += 5
    if has_output:
        score += 4
    if has_cached:
        score += 3
    if has_total:
        score += 2
    if input_tokens > 0:
        score += 1
    if output_tokens > 0:
        score += 1
    if cached_tokens > 0:
        score += 1

    return score, input_tokens, output_tokens, cached_tokens


@typechecked
def collect_usage_candidates(payload: object) -> list[tuple[int, int, int, int]]:
    """Collect usage candidates from available values.

    Args:
        payload (object): Value for payload.

    Returns:
        list[tuple[int, int, int, int]]: List containing computed output items.
    """
    candidates: list[tuple[int, int, int, int]] = []
    stack: list[object] = [payload]

    while stack:
        node = stack.pop()
        if isinstance(node, dict):
            parsed_candidate = score_usage_candidate(node)
            if parsed_candidate is not None:
                candidates.append(parsed_candidate)
            for value in node.values():
                stack.append(value)
            continue

        if isinstance(node, list):
            for item in node:
                stack.append(item)

    return candidates


@typechecked
def extract_usage_from_message_row(message_row: dict[str, Any]) -> tuple[int, int, int]:
    """Extract usage from message row from the provided data.

    Args:
        message_row (dict[str, Any]): Value for message row.

    Returns:
        tuple[int, int, int]: Tuple containing computed output values.
    """
    candidates = collect_usage_candidates(message_row)
    if not candidates:
        return 0, 0, 0

    best_candidate = max(
        candidates,
        key=lambda item: (item[0], item[1] + item[2] + item[3], item[3], item[1], item[2]),
    )
    return best_candidate[1], best_candidate[2], best_candidate[3]


@typechecked
def extract_model_name_from_usage_log_payload(log_payload: dict[str, Any]) -> str:
    """Extract model name from usage log payload from the provided data.

    Args:
        log_payload (dict[str, Any]): Value for log payload.

    Returns:
        str: String result produced by this function.
    """
    request_raw = log_payload.get("request")
    if isinstance(request_raw, dict):
        request_model = normalize_model_name_for_lookup(str(request_raw.get("model") or ""))
        if request_model:
            return request_model
        request_model_name = normalize_model_name_for_lookup(str(request_raw.get("model_name") or ""))
        if request_model_name:
            return request_model_name
        request_model_name_camel = normalize_model_name_for_lookup(str(request_raw.get("modelName") or ""))
        if request_model_name_camel:
            return request_model_name_camel

    top_level_model = normalize_model_name_for_lookup(str(log_payload.get("model") or ""))
    if top_level_model:
        return top_level_model
    top_level_model_name = normalize_model_name_for_lookup(str(log_payload.get("model_name") or ""))
    if top_level_model_name:
        return top_level_model_name

    response_raw = log_payload.get("response")
    if isinstance(response_raw, dict):
        response_model = normalize_model_name_for_lookup(str(response_raw.get("model") or ""))
        if response_model:
            return response_model
        response_model_name = normalize_model_name_for_lookup(str(response_raw.get("model_name") or ""))
        if response_model_name:
            return response_model_name
        response_model_name_camel = normalize_model_name_for_lookup(str(response_raw.get("modelName") or ""))
        if response_model_name_camel:
            return response_model_name_camel

    return ""


@typechecked
def extract_timestamp_from_gemini_log_file_name(file_name: str) -> str:
    """Extract timestamp from gemini log file name from the provided data.

    Args:
        file_name (str): File-system path or file name used by this function.

    Returns:
        str: String result produced by this function.
    """
    normalized_file_name = str(file_name or "").strip()
    name_match = re.fullmatch(
        r"(\\d{4}-\\d{2}-\\d{2})_(\\d{2})-(\\d{2})-(\\d{2})(?:_[A-Za-z0-9]+)?\\.log",
        normalized_file_name,
    )
    if name_match is None:
        return ""

    date_part = str(name_match.group(1))
    hour_part = str(name_match.group(2))
    minute_part = str(name_match.group(3))
    second_part = str(name_match.group(4))
    return f"{date_part} {hour_part}:{minute_part}:{second_part}"


@typechecked
def format_decimal_cost(value: Decimal) -> str:
    """Format decimal cost for output or display.

    Args:
        value (Decimal): Value for value.

    Returns:
        str: String result produced by this function.
    """
    quantized_value = value.quantize(Decimal("0.0000000001"), rounding=ROUND_HALF_UP)
    return format(quantized_value, "f")
