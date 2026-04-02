import json
import logging
from typing import Any

from typeguard import typechecked  # type: ignore


@typechecked
def extract_json_after_think(text: str) -> dict[str, Any]:
    """Extract JSON from model output, handling </think> and markdown code blocks."""
    logger = logging.getLogger(__name__)

    if not text:
        logger.error("extract_json_after_think: Received empty text from model")
        raise ValueError("Empty response from model")

    if "</think>" in text:
        text = text.split("</think>", 1)[1]

    text = text.strip()
    if not text:
        logger.error("extract_json_after_think: Text is empty after removing </think>")
        raise ValueError("Empty response after removing </think> tag")

    try:
        parsed = json.loads(text)
        if isinstance(parsed, dict):
            return parsed
        raise json.JSONDecodeError("Parsed JSON is not an object", text, 0)
    except json.JSONDecodeError:
        pass

    if "```json" in text:
        try:
            json_str = text.split("```json", 1)[1].split("```", 1)[0].strip()
            parsed = json.loads(json_str)
            if isinstance(parsed, dict):
                return parsed
            raise json.JSONDecodeError("Parsed JSON is not an object", json_str, 0)
        except (IndexError, json.JSONDecodeError):
            pass

    if "```" in text:
        try:
            json_str = text.split("```", 1)[1].split("```", 1)[0].strip()
            parsed = json.loads(json_str)
            if isinstance(parsed, dict):
                return parsed
            raise json.JSONDecodeError("Parsed JSON is not an object", json_str, 0)
        except (IndexError, json.JSONDecodeError):
            pass

    if "{" in text:
        json_start = text.find("{")
        json_end = text.rfind("}") + 1
        if json_start >= 0 and json_end > json_start:
            json_str = text[json_start:json_end]
            parsed = json.loads(json_str)
            if isinstance(parsed, dict):
                return parsed
            raise json.JSONDecodeError("Parsed JSON is not an object", json_str, 0)

    raise json.JSONDecodeError("Could not extract valid JSON object from response", text, 0)
