from typing import Any


def is_admin_group(value: Any) -> bool:
    if isinstance(value, str):
        normalized = value.strip()
        if not normalized:
            return False
        groups = [part.strip().upper() for part in normalized.split(",")]
        return "ADMIN" in groups
    if isinstance(value, (list, tuple, set)):
        return any(
            isinstance(item, str) and item.strip().upper() == "ADMIN"
            for item in value
        )
    return False
