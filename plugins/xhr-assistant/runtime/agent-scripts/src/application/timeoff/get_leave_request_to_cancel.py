import json

from src.core.models.request_context import RequestContext
from src.core.interfaces.http_client import HttpClient
from src.core.models.types import Header
from src.shared.normalize import clean_text
from src.shared.result import ok_result, error_result

from src.shared.http import format_error, request_json


def _extract_type_map(items):
    type_map = {}
    if not isinstance(items, list):
        return type_map

    for item in items:
        if not isinstance(item, dict):
            continue
        type_id = item.get("id")
        name = item.get("name")
        if type_id and name:
            type_map[type_id] = name
    return type_map


async def _fetch_type_names(client, url, headers):
    status_code, payload = await request_json(client, "GET", url, headers=headers)

    if status_code >= 400:
        raise RuntimeError(json.dumps(format_error(payload), ensure_ascii=False))

    if isinstance(payload, dict):
        return _extract_type_map(payload.get("data"))
    return {}


async def run(task_args, context: RequestContext, http_client: HttpClient):
    api_base_url = context.api_base_url
    headers = context.headers
    employee_id = context.request_headers.get(Header.X_EMPLOYEE_ID)

    task_args = task_args if isinstance(task_args, dict) else {}
    start_date = clean_text(task_args.get("start_date") or task_args.get("startDate"))
    end_date = clean_text(task_args.get("end_date") or task_args.get("endDate"))

    query_params = {}
    if employee_id:
        query_params["employeeId"] = employee_id
    if start_date:
        query_params["startDate"] = start_date
    if end_date:
        query_params["endDate"] = end_date
    query_params["status"] = "PENDING"

    requests_url = f"{api_base_url}/v1/to/time-off-requests/by-date-range"
    types_url = f"{api_base_url}/v1/to/time-off-types"

    type_name_lookup = {}
    type_lookup_error = None
    async with http_client.session() as client:
        try:
            status_code, payload = await request_json(client, "GET", requests_url, params=query_params, headers=headers)
        except Exception as exc:
            return error_result(str(format_error(exc=exc)),)

        try:
            type_name_lookup = await _fetch_type_names(client, types_url, headers)
        except Exception as exc:
            type_lookup_error = {"message": str(exc)}

    if isinstance(payload, dict):
        requests = payload.get("data")
        if not isinstance(requests, list):
            requests = []
        meta = payload.get("meta")
    else:
        requests = []
        meta = None

    formatted_requests = []
    for request in requests:
        type_id = request.get("time_off_type_id")
        type_name = request.get("time_off_type_name")
        if not type_name and type_id:
            type_name = type_name_lookup.get(type_id)

        formatted_requests.append({
            "request_id": request.get("id"),
            "time_off_type": type_name,
            "start_date": request.get("start_date"),
            "end_date": request.get("end_date"),
            "note": request.get("notes"),
        })

    request_ids_for_next_action = [
        entry["request_id"] for entry in formatted_requests if entry.get("request_id")
    ]

    if formatted_requests and request_ids_for_next_action:
        request_id_flags = " ".join(
            f"--request-ids {request_id}" for request_id in request_ids_for_next_action
        )
        next_action = (
            "ask user to confirm and then call exec with: "
            f'{{"command": "python skills/timeoff/cancel_request/scripts/cancel_request.py {request_id_flags}"}}'
        )
    else:
        next_action = "no_leave_requests_found"

    if status_code >= 400:
        return error_result(str(format_error(payload)),)

    if type_lookup_error:
        return error_result(str(type_lookup_error),)

    return ok_result({
        "data": formatted_requests,
        "nextAction": next_action,
        "meta": meta,
        "query": query_params,
    })
