import json

from src.core.models.request_context import RequestContext
from src.core.interfaces.http_client import HttpClient
from src.shared.normalize import clean_int, clean_text
from src.shared.result import ok_result, error_result


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


async def run(task_args, context: RequestContext, http_client: HttpClient):
    api_base_url = context.api_base_url
    headers = context.headers

    args = task_args if isinstance(task_args, dict) else {}
    page = _to_int(args.get("page"), 0)
    size = _to_int(args.get("size"), 20)
    name = clean_text(args.get("name"))

    page = max(page, 0)
    size = max(size, 1)

    params = {
        "page": page,
        "size": size,
        "sort": "createdAt,desc",
    }
    if name:
        params["name.contains"] = name

    url = f"{api_base_url}/v1/vdr/data-rooms"

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

    formatted_data = []
    if not isinstance(data, list):
        data = []

    for item in data:
        if not isinstance(item, dict):
            continue
        formatted_item = {
            "data_room_id": item.get("id"),
            "data_room_name": item.get("name"),
            "description": item.get("description"),
            "status": item.get("status"),
            "sharing_mode": item.get("sharing_mode"),
            "public_access_token": item.get("public_access_token"),
            "public_slug": item.get("public_slug"),
            "auto_approve": item.get("auto_approve"),
            "public_link": item.get("public_link"),
            "updated_at": item.get("updated_at"),
            "shared_with": item.get("shared_with"),
            "total_shared_count": item.get("total_shared_count"),
        }
        formatted_data.append(formatted_item)

    data_count = len(formatted_data)

    if response.status_code < 200 or response.status_code >= 300:
        return error_result(f"Data rooms request failed: {response.status_code} {str(payload)}",)

    return ok_result({
        "data_count": data_count,
        "data": formatted_data,
        "meta": meta,
        "filters": {
            "page": page,
            "size": size,
            "name": name,
            "sort": "createdAt,desc",
        },
    })
