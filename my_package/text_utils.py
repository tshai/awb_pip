import re

from typeguard import typechecked  # type: ignore


@typechecked
def contains_hebrew_text(text: str) -> bool:
    """Compute contains hebrew text for this workflow.

    Args:
        text (str): Value for text.

    Returns:
        bool: True when the condition is met; otherwise False.
    """
    for ch in str(text or ""):
        if "\u0590" <= ch <= "\u05FF":
            return True
    return False


@typechecked
def build_invalid_json_reply(user_message: str) -> str:
    """Build invalid json reply from the provided inputs.

    Args:
        user_message (str): Value for user message.

    Returns:
        str: String result produced by this function.
    """
    if contains_hebrew_text(user_message):
        return "התקבלה תשובה לא תקינה מהמודל ולכן לא בוצע שינוי. אפשר לנסות שוב באותה בקשה?"
    return "The model returned an invalid response format, so no change was applied. Please retry the same request."


@typechecked
def normalize_whitespace_lower(text: str) -> str:
    """Normalize whitespace lower into a consistent format.

    Args:
        text (str): Value for text.

    Returns:
        str: String result produced by this function.
    """
    compact = re.sub(r"\s+", " ", str(text or "").strip().lower())
    return compact
