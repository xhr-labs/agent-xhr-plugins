from src.core.models.request_context import RequestContext
from src.core.interfaces.http_client import HttpClient
from src.shared.normalize import clean_text
from src.shared.result import ok_result, error_result
from src.shared.http import format_error, request_json


async def run(task_args, context: RequestContext, http_client: HttpClient):
    api_base_url = context.api_base_url
    headers = context.headers

    task_args = task_args if isinstance(task_args, dict) else {}
    employee_id = clean_text(task_args.get("employee_id") or task_args.get("employeeId"))
    if not employee_id:
        return error_result("employee_id_required")

    time_off_type_id = clean_text(task_args.get("time_off_type_id") or task_args.get("timeOffTypeId"))

    endpoint = f"{api_base_url}/v1/to/time-off-ledger-entries"
    query_params = {"employeeId.equals": employee_id}
    if time_off_type_id:
        query_params["timeOffTypeId.equals"] = time_off_type_id

    async with http_client.session() as client:
        try:
            status_code, payload = await request_json(client, "GET", endpoint, params=query_params, headers=headers)
        except Exception as exc:
            return error_result(str(format_error(exc=exc)))

    if status_code >= 400:
        return error_result(str(format_error(payload)))

    entries = payload.get("data") if isinstance(payload, dict) else payload
    if not isinstance(entries, list):
        entries = []

    formatted = []
    for e in entries:
        if not isinstance(e, dict):
            continue
        formatted.append({
            "id": e.get("id"),
            "event_type": e.get("event_type") or e.get("eventType"),
            "amount": e.get("amount"),
            "description": e.get("description") or e.get("notes"),
            "created_at": e.get("created_at") or e.get("createdAt"),
            "balance_after": e.get("balance_after") or e.get("balanceAfter"),
        })

    return ok_result({
        "employee_id": employee_id,
        "entries_count": len(formatted),
        "ledger_entries": formatted,
        "query": query_params,
    })
