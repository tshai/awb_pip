import json
from typing import Any

from typeguard import typechecked  # type: ignore


@typechecked
def extract_json_candidate(text: str) -> str:
    raw = str(text or "").strip()
    if not raw:
        return ""

    if "</think>" in raw:
        raw = raw.split("</think>", 1)[1].strip()

    if raw.startswith("```") and raw.endswith("```"):
        lines = raw.splitlines()
        if len(lines) >= 3:
            raw = "\n".join(lines[1:-1]).strip()

    if "```json" in raw:
        try:
            return raw.split("```json", 1)[1].split("```", 1)[0].strip()
        except Exception:
            pass

    if "```" in raw:
        try:
            return raw.split("```", 1)[1].split("```", 1)[0].strip()
        except Exception:
            pass

    if raw.startswith("{") and raw.endswith("}"):
        return raw

    if "{" in raw and "}" in raw:
        start = raw.find("{")
        end = raw.rfind("}") + 1
        if start >= 0 and end > start:
            return raw[start:end].strip()

    return raw


@typechecked
def parse_model_json_object(text: str) -> dict[str, Any]:
    normalized_text = str(text or "").strip()
    if not normalized_text:
        raise ValueError("Model returned empty response")

    candidate = extract_json_candidate(normalized_text)
    if not candidate:
        raise ValueError("Model returned empty response")

    try:
        parsed = json.loads(candidate)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Model returned invalid JSON (pos={exc.pos}, line={exc.lineno}, col={exc.colno})"
        ) from exc

    if not isinstance(parsed, dict):
        raise ValueError("Model returned JSON that is not an object")
    return parsed
