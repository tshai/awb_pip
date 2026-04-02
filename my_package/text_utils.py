import re

from typeguard import typechecked  # type: ignore


@typechecked
def contains_hebrew_text(text: str) -> bool:
    for ch in str(text or ""):
        if "\u0590" <= ch <= "\u05FF":
            return True
    return False


@typechecked
def build_invalid_json_reply(user_message: str) -> str:
    if contains_hebrew_text(user_message):
        return "התקבלה תשובה לא תקינה מהמודל ולכן לא בוצע שינוי. אפשר לנסות שוב באותה בקשה?"
    return "The model returned an invalid response format, so no change was applied. Please retry the same request."


@typechecked
def normalize_whitespace_lower(text: str) -> str:
    compact = re.sub(r"\s+", " ", str(text or "").strip().lower())
    return compact
