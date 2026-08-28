import uuid
from typing import Any, Iterable, List, Optional


def clean_text(value: Any) -> Optional[str]:
    if isinstance(value, str):
        trimmed = value.strip()
        return trimmed or None
    return None


def clean_int(value: Any) -> Optional[int]:
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        trimmed = value.strip()
        if trimmed.isdigit():
            try:
                return int(trimmed)
            except ValueError:
                return None
    return None


def clean_float(value: Any) -> Optional[float]:
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        trimmed = value.strip()
        try:
            return float(trimmed)
        except ValueError:
            return None
    return None


def normalize_list(value: Any) -> List[str]:
    if value is None:
        return []

    if isinstance(value, (list, tuple, set)):
        candidates: Iterable[Any] = list(value)
    else:
        candidates = [value]

    normalized: List[str] = []
    for candidate in candidates:
        if candidate is None:
            continue
        if isinstance(candidate, str):
            parts = [part.strip() for part in candidate.split(",")]
            normalized.extend([part for part in parts if part])
        else:
            normalized.append(str(candidate))
    return normalized


def to_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value

    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"1", "true", "yes", "y"}:
            return True
        if lowered in {"0", "false", "no", "n"}:
            return False

    if isinstance(value, (int, float)):
        return value != 0

    return False


def get_nested_value(payload: Any, path: Iterable[str]) -> Any:
    current = payload
    for key in path:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def is_uuid(value: Any) -> bool:
    if not value:
        return False
    try:
        uuid.UUID(str(value))
        return True
    except (ValueError, TypeError):
        return False
