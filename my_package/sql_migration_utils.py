from typeguard import typechecked  # type: ignore


@typechecked
def qname(name: str) -> str:
    return "`" + name.replace("`", "``") + "`"


@typechecked
def qstr(value: str) -> str:
    return "'" + value.replace("\\", "\\\\").replace("'", "\\'") + "'"


@typechecked
def is_target_column(col_name: str) -> bool:
    return col_name == "id" or col_name.endswith("_id")


@typechecked
def already_big_unsigned(col_type: str) -> bool:
    normalized = " ".join(col_type.lower().split())
    return normalized.startswith("bigint") and "unsigned" in normalized
