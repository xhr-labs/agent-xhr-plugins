from src.core.models.request_context import RequestContext
from src.core.interfaces.http_client import HttpClient
from src.shared.result import ok_result, error_result

from src.shared.http import format_error, request_json


async def run(task_args, context: RequestContext, http_client: HttpClient):
    api_base_url = context.api_base_url
    headers = context.headers

    task_args = task_args if isinstance(task_args, dict) else {}
    page = task_args.get("page", 0)
    size = task_args.get("size", 20)
    try:
        page = int(page)
    except Exception:
        page = 0
    try:
        size = int(size)
    except Exception:
        size = 20

    page = max(page, 0)
    size = min(max(size, 1), 200)

    url = f"{api_base_url}/v1/to/time-off-types"
    params = {"page": page, "size": size}

    async with http_client.session() as client:
        try:
            status_code, payload = await request_json(client, "GET", url, params=params, headers=headers)
        except Exception as exc:
            return error_result(str(format_error(exc=exc)),)

    if isinstance(payload, dict):
        data = payload.get("data") or []
        meta = payload.get("meta")
    else:
        data = []
        meta = None

    output = []
    if isinstance(data, list):
        for item in data:
            if not isinstance(item, dict):
                continue
            output.append({
                "time_off_type_id": item.get("id"),
                "time_off_type_name": item.get("name"),
                "accrual_rule": item.get("accrual_rule"),
                "icon": item.get("icon"),
                "total_days_per_year": item.get("total_days_per_year"),
                "allocation_type": item.get("allocation_type"),
                "can_delete": item.get("can_delete"),
            })

    if status_code >= 400:
        return error_result(str(format_error(payload)),)

    return ok_result({
        "data": output,
        "meta": meta,
        "query": {"page": page, "size": size},
    })
