from typing import Any, Dict, Iterable, List, Tuple


def _format_status(status: Dict[str, Any]) -> Dict[str, Any]:
    status_id = status.get("id")
    if not status_id:
        return {}
    return {
        "id": status_id,
        "name": status.get("name"),
        "translate_key": status.get("translate_key"),
    }


def resolve_status_filters(
    statuses: Iterable[Dict[str, Any]],
    include_completed: bool,
    requested_ids: Iterable[str],
    requested_keys: Iterable[str],
    requested_names: Iterable[str],
) -> Tuple[List[str], List[Dict[str, Any]], List[Dict[str, Any]]]:
    lookup_by_id: Dict[str, Dict[str, Any]] = {}
    lookup_by_key: Dict[str, Dict[str, Any]] = {}
    lookup_by_name: Dict[str, Dict[str, Any]] = {}
    available_statuses: List[Dict[str, Any]] = []
    default_statuses: List[Dict[str, Any]] = []

    for status in statuses:
        if not isinstance(status, dict):
            continue

        status_id = status.get("id")
        if not status_id:
            continue

        translate_key = (status.get("translate_key") or "").lower()
        status_name = (status.get("name") or "").strip().lower()

        lookup_by_id[status_id] = status
        if translate_key:
            lookup_by_key[translate_key] = status
        if status_name:
            lookup_by_name[status_name] = status

        formatted = _format_status(status)
        if formatted:
            available_statuses.append(formatted)

        include_by_default = True
        if not include_completed:
            last = translate_key.split(".")[-1] if translate_key else ""
            if last in {"done", "completed"}:
                include_by_default = False

        if include_by_default:
            default_statuses.append(status)

    selected_status_objects: List[Dict[str, Any]] = []

    def _append_status(status_obj: Dict[str, Any]) -> None:
        status_id_value = status_obj.get("id")
        if not status_id_value:
            return
        for existing in selected_status_objects:
            if existing.get("id") == status_id_value:
                return
        selected_status_objects.append(status_obj)

    for status_id in requested_ids:
        candidate = lookup_by_id.get(status_id)
        if candidate:
            _append_status(candidate)

    for key in requested_keys:
        candidate = lookup_by_key.get(key.lower())
        if candidate:
            _append_status(candidate)

    for name in requested_names:
        candidate = lookup_by_name.get(name.lower())
        if candidate:
            _append_status(candidate)

    if not selected_status_objects:
        selected_status_objects = default_statuses

    resolved_status_ids: List[str] = []
    resolved_status_details: List[Dict[str, Any]] = []
    for status in selected_status_objects:
        formatted = _format_status(status)
        if not formatted:
            continue
        resolved_status_ids.append(formatted["id"])
        resolved_status_details.append(formatted)

    return resolved_status_ids, resolved_status_details, available_statuses
