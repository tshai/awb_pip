from typeguard import typechecked  # type: ignore


@typechecked
def parse_bool_flag(raw_value: str) -> bool:
    normalized = raw_value.strip().lower()
    if normalized == "true":
        return True
    if normalized == "false":
        return False
    raise ValueError("run-llm must be true or false")
