from typeguard import typechecked  # type: ignore


@typechecked
def env_flag(value: str) -> bool:
    normalized = str(value).strip().lower()
    return normalized in {"1", "true", "yes", "on"}
