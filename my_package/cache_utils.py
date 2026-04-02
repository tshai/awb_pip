from typeguard import typechecked  # type: ignore


@typechecked
def extract_google_cache_test_response_text(response_obj: object) -> str:
    response_text = str(getattr(response_obj, "text", "") or "").strip()
    if response_text:
        return response_text

    candidates = getattr(response_obj, "candidates", None)
    if not isinstance(candidates, list):
        return ""

    collected_parts: list[str] = []
    for candidate in candidates:
        content = getattr(candidate, "content", None)
        parts = getattr(content, "parts", None)
        if not isinstance(parts, list):
            continue
        for part in parts:
            part_text = str(getattr(part, "text", "") or "").strip()
            if part_text:
                collected_parts.append(part_text)

    return "\n".join(collected_parts).strip()


@typechecked
def to_serializable_cached_value(value: object) -> object:
    if value is None:
        return None
    if isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, dict):
        normalized_dict: dict[str, object] = {}
        for key, item in value.items():
            normalized_dict[str(key)] = to_serializable_cached_value(item)
        return normalized_dict
    if isinstance(value, (list, tuple, set)):
        normalized_list: list[object] = []
        for item in value:
            normalized_list.append(to_serializable_cached_value(item))
        return normalized_list

    to_dict_fn = getattr(value, "to_dict", None)
    if callable(to_dict_fn):
        try:
            dict_value = to_dict_fn()
            if isinstance(dict_value, dict):
                return to_serializable_cached_value(dict_value)
        except Exception:
            pass

    model_dump_fn = getattr(value, "model_dump", None)
    if callable(model_dump_fn):
        try:
            dict_value = model_dump_fn()
            if isinstance(dict_value, dict):
                return to_serializable_cached_value(dict_value)
        except Exception:
            pass

    raw_dict = getattr(value, "__dict__", None)
    if isinstance(raw_dict, dict) and raw_dict:
        normalized_attrs: dict[str, object] = {}
        for key, item in raw_dict.items():
            normalized_key = str(key or "").strip()
            if not normalized_key or normalized_key.startswith("_"):
                continue
            normalized_attrs[normalized_key] = to_serializable_cached_value(item)
        if normalized_attrs:
            return normalized_attrs

    return str(value)


@typechecked
def extract_google_cached_system_instruction_text(cached_content_obj: object) -> str:
    system_instruction = getattr(cached_content_obj, "system_instruction", None)
    if system_instruction is None:
        return ""

    if isinstance(system_instruction, str):
        return system_instruction.strip()

    if isinstance(system_instruction, dict):
        parts_value = system_instruction.get("parts")
        if isinstance(parts_value, list):
            text_parts: list[str] = []
            for part in parts_value:
                if isinstance(part, dict):
                    part_text = str(part.get("text") or "").strip()
                    if part_text:
                        text_parts.append(part_text)
                elif isinstance(part, str):
                    part_text = part.strip()
                    if part_text:
                        text_parts.append(part_text)
            return "\n".join(text_parts).strip()
        return str(system_instruction).strip()

    parts = getattr(system_instruction, "parts", None)
    if isinstance(parts, list):
        text_parts: list[str] = []
        for part in parts:
            part_text = str(getattr(part, "text", "") or "").strip()
            if part_text:
                text_parts.append(part_text)
        return "\n".join(text_parts).strip()

    return str(system_instruction).strip()
