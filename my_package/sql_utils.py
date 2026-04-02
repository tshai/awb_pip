import json
from typing import Any, Iterable

from typeguard import typechecked  # type: ignore

WRITE_PREFIXES = {
    "INSERT",
    "UPDATE",
    "DELETE",
    "REPLACE",
    "CREATE",
    "ALTER",
    "DROP",
    "TRUNCATE",
    "RENAME",
    "GRANT",
    "REVOKE",
}


@typechecked
def parse_params(raw: str | None) -> Any:
    """Parse params into a structured Python value.

    Args:
        raw (str | None): Value for raw.

    Returns:
        Any: Computed result from this function.
    """
    if raw is None or raw == "":
        return None
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in params: {exc}") from exc

    if isinstance(parsed, list):
        return tuple(parsed)
    return parsed


@typechecked
def first_keyword(sql: str) -> str:
    """Compute first keyword for this workflow.

    Args:
        sql (str): Value for sql.

    Returns:
        str: String result produced by this function.
    """
    stripped = sql.strip()
    if not stripped:
        return ""
    return stripped.split(None, 1)[0].upper()


@typechecked
def is_write_statement(sql: str) -> bool:
    """Return whether write statement is true for the given input.

    Args:
        sql (str): Value for sql.

    Returns:
        bool: True when the condition is met; otherwise False.
    """
    return first_keyword(sql) in WRITE_PREFIXES


@typechecked
def split_sql_statements(sql_blob: str) -> list[str]:
    """Compute split sql statements for this workflow.

    Args:
        sql_blob (str): Value for sql blob.

    Returns:
        list[str]: List containing computed output items.
    """
    chunks = [part.strip() for part in sql_blob.split(";")]
    return [chunk for chunk in chunks if chunk]


@typechecked
def ensure_write_allowed(statements: Iterable[str], allow_write: bool) -> None:
    """Ensure write allowed satisfies required constraints.

    Args:
        statements (Iterable[str]): Value for statements.
        allow_write (bool): Boolean flag that controls allow write behavior.

    Returns:
        None: This function does not return a value.
    """
    has_write = any(is_write_statement(statement) for statement in statements)
    if has_write and not allow_write:
        raise PermissionError("Write/DDL statement detected. Re-run with write permission.")
