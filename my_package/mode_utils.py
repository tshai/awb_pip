from typeguard import typechecked  # type: ignore


@typechecked
def normalize_signup_mode(mode: str, default_mode: str) -> str:
    valid_modes = {"allow", "block"}
    normalized_default = str(default_mode or "").strip().lower()
    if normalized_default not in valid_modes:
        normalized_default = "allow"

    normalized = str(mode or "").strip().lower()
    if normalized in valid_modes:
        return normalized
    return normalized_default


@typechecked
def normalize_namecom_dns_mode(mode: str, fallback: str) -> str:
    normalized_fallback = str(fallback or "").strip().lower()
    if normalized_fallback not in {"production", "dev"}:
        normalized_fallback = "production"

    normalized = str(mode or "").strip().lower()
    if normalized in {"production", "prod", "live"}:
        return "production"
    if normalized in {"dev", "test", "sandbox"}:
        return "dev"
    return normalized_fallback


@typechecked
def normalize_cardcom_mode(mode: str, default_mode: str) -> str:
    valid_modes = {"live", "test"}
    normalized_default = str(default_mode or "").strip().lower()
    if normalized_default not in valid_modes:
        normalized_default = "live"

    normalized = str(mode or "").strip().lower()
    if normalized in valid_modes:
        return normalized
    return normalized_default
