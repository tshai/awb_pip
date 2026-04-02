import fnmatch

from typeguard import typechecked  # type: ignore


@typechecked
def parse_semicolon_list(raw: str) -> list[str]:
    return [item.strip() for item in raw.split(";") if item.strip()]


@typechecked
def build_excludes(filemask: str) -> tuple[set[str], set[str], list[str]]:
    raw = filemask.strip()
    if raw.startswith("|"):
        raw = raw[1:]
    patterns = parse_semicolon_list(raw)

    exclude_dirs: set[str] = set()
    exclude_exact_files: set[str] = set()
    exclude_glob_files: list[str] = []

    for item in patterns:
        token = item.replace("\\", "/").strip()
        if not token:
            continue

        if token.endswith("/"):
            part = token.rstrip("/")
            dir_name = part.split("/")[-1].strip()
            if dir_name:
                exclude_dirs.add(dir_name.lower())
            continue

        if "*" in token or "?" in token:
            exclude_glob_files.append(token)
        else:
            exclude_exact_files.add(token.lower())

    return exclude_dirs, exclude_exact_files, exclude_glob_files


@typechecked
def should_skip_file(file_name: str, rel_posix: str, exact_files: set[str], glob_files: list[str]) -> bool:
    lower_name = file_name.lower()
    lower_rel = rel_posix.lower()
    if lower_name in exact_files or lower_rel in exact_files:
        return True
    for pattern in glob_files:
        lowered_pattern = pattern.lower()
        if fnmatch.fnmatch(lower_name, lowered_pattern) or fnmatch.fnmatch(lower_rel, lowered_pattern):
            return True
    return False


@typechecked
def safe_int(value: str, fallback: int) -> int:
    try:
        return int(str(value).strip())
    except Exception:
        return fallback
