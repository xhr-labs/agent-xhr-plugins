from src.core.models.request_context import RequestContext
from src.core.interfaces.http_client import HttpClient
from src.shared.normalize import clean_text, to_bool
from src.shared.result import ok_result, error_result


def _to_int(value, default):
    try:
        return int(value)
    except Exception:
        return default


def _format_shift(item):
    if not isinstance(item, dict):
        return None
    return {
        "shift_id": item.get("id"),
        "name": item.get("name"),
        "description": item.get("description"),
        "is_active": item.get("is_active"),
        "apply_public_holiday_target_hours": item.get("apply_public_holiday_target_hours"),
        "employee_count": item.get("employee_count"),
        "created_at": item.get("created_at"),
        "updated_at": item.get("updated_at"),
        "raw": item,
    }


async def run(task_args, context: RequestContext, http_client: HttpClient):
    api_base_url = context.api_base_url
    headers = context.headers
    args = task_args if isinstance(task_args, dict) else {}

    shift_id = clean_text(args.get("shift_id") or args.get("id"))
    shift_name = clean_text(args.get("shift_name") or args.get("name"))
    search_keyword = clean_text(args.get("search_keyword")) or shift_name
    sort_value = clean_text(args.get("sort"))
    page = max(_to_int(args.get("page"), 0), 0)
    size = min(max(_to_int(args.get("size"), 20), 1), 100)

    is_active_value = args.get("is_active")
    if is_active_value is None:
        is_active_value = args.get("isActive")
    is_active = None if is_active_value is None else to_bool(is_active_value)

    url = f"{api_base_url}/v1/atd/shifts"
    params = {
        "page": page,
        "size": size,
    }
    if search_keyword:
        params["search_keyword"] = search_keyword
    if is_active is not None:
        params["is_active"] = str(is_active).lower()
    if sort_value:
        params["sort"] = sort_value

    async with http_client.session() as client:
        response = await client.get(url, headers=headers, params=params)
        status_code = response.status_code
        try:
            payload = response.json()
        except Exception:
            payload = {}

    if status_code < 200 or status_code >= 300:
        return error_result(f"Get shifts failed: {status_code}")

    items = payload.get("data") or [] if isinstance(payload, dict) else []
    shifts = []
    for item in items:
        formatted = _format_shift(item)
        if formatted:
            shifts.append(formatted)

    exact_matches = shifts
    if shift_id:
        exact_matches = [item for item in exact_matches if item.get("shift_id") == shift_id]
    if shift_name:
        exact_matches = [item for item in exact_matches if (item.get("name") or "").strip().lower() == shift_name.strip().lower()]

    return ok_result({
        "shifts_count": len(shifts),
        "shifts": shifts,
        "exact_matches_count": len(exact_matches),
        "exact_matches": exact_matches,
        "filters": {
            "shift_id": shift_id,
            "shift_name": shift_name,
            "search_keyword": search_keyword,
            "is_active": is_active,
            "page": page,
            "size": size,
            "sort": sort_value,
        },
    })
