from src.core.models.request_context import RequestContext
from src.core.interfaces.http_client import HttpClient
from src.shared.normalize import clean_int, clean_text
from src.shared.result import ok_result, error_result
import src.application.vdr.list_data_rooms as list_data_rooms


def _to_int(value, default):
    if value is None:
        return default
    cleaned = clean_int(value)
    if cleaned is not None:
        return cleaned
    try:
        return int(value)
    except Exception:
        return default


def _resolve_data_room_id(data_rooms, requested_name):
    if not isinstance(data_rooms, list) or not requested_name:
        return None

    requested_lower = requested_name.lower()
    for item in data_rooms:
        if not isinstance(item, dict):
            continue
        name = item.get("data_room_name")
        if isinstance(name, str) and name.lower() == requested_lower:
            return item.get("data_room_id")

    first = data_rooms[0] if data_rooms else None
    if isinstance(first, dict):
        return first.get("data_room_id")
    return None


def _to_created_at(value, is_start):
    cleaned = clean_text(value)
    if not cleaned:
        return None
    if "T" in cleaned:
        return cleaned
    if is_start:
        return f"{cleaned}T00:00:00.000Z"
    return f"{cleaned}T23:59:59.999Z"


async def run(task_args, context: RequestContext, http_client: HttpClient):
    api_base_url = context.api_base_url
    headers = context.headers

    args = task_args if isinstance(task_args, dict) else {}
    page = _to_int(args.get("page"), 0)
    size = _to_int(args.get("size"), 20)
    data_room = clean_text(args.get("dataRoom"))
    start_date = _to_created_at(args.get("startDate"), True)
    end_date = _to_created_at(args.get("endDate"), False)

    page = max(page, 0)
    size = max(size, 1)

    data_room_id = None
    if data_room:
        data_room_payload = await list_data_rooms.run({
            "page": 0,
            "size": 20,
            "name": data_room,
        }, context, http_client)
        if isinstance(data_room_payload, dict) and data_room_payload.get("ok") is True:
            data_rooms = ((data_room_payload.get("data") or {}).get("data")) or []
        else:
            data_rooms = []
        data_room_id = _resolve_data_room_id(data_rooms, data_room)

        if not data_room_id:
            return error_result("data_room_not_found",)

    params = {
        "page": page,
        "size": size,
        "sort": "actionTimestamp,desc",
    }
    if data_room_id:
        params["dataRoomId.equals"] = data_room_id
    if start_date:
        params["createdAt.greaterThanOrEqual"] = start_date
    if end_date:
        params["createdAt.lessThanOrEqual"] = end_date

    url = f"{api_base_url}/v1/vdr/audit-logs"

    async with http_client.session() as client:
        response = await client.get(url, headers=headers, params=params)
        try:
            payload = response.json()
        except Exception:
            payload = {}

    if isinstance(payload, dict):
        data = payload.get("data") or []
        meta = payload.get("meta")
    else:
        data = []
        meta = None

    data_count = len(data) if isinstance(data, list) else 0

    if response.status_code < 200 or response.status_code >= 300:
        return error_result(f"Audit logs request failed: {response.status_code} {str(payload)}",)

    return ok_result({
        "data_count": data_count,
        "data": data,
        "meta": meta,
        "filters": {
            "page": page,
            "size": size,
            "dataRoom": data_room,
            "dataRoomId": data_room_id,
            "sort": "actionTimestamp,desc",
            "startDate": start_date,
            "endDate": end_date,
        },
    })
