from src.core.models.request_context import RequestContext
from src.core.interfaces.http_client import HttpClient
from src.shared.normalize import normalize_list
from src.shared.result import ok_result, error_result


def _format_status(status):
    if not isinstance(status, dict):
        return None
    status_id = status.get("id")
    if not status_id:
        return None
    return {
        "status_id": status_id,
        "status_name": status.get("name"),
        "status_key": status.get("translate_key"),
        "status_type": status.get("status_type"),
        "total_tasks": status.get("total_tasks"),
    }


async def run(task_args, context: RequestContext, http_client: HttpClient):
    api_base_url = context.api_base_url
    headers = context.headers

    task_args = task_args if isinstance(task_args, dict) else {}
    args = task_args
    if "status_type" in args and "statusType" not in args:
        args["statusType"] = args.get("status_type")
    if "status_types" in args and "statusTypes" not in args:
        args["statusTypes"] = args.get("status_types")
    statuses_url = f"{api_base_url}/v1/pm/statuses"
    status_types_filter = normalize_list(task_args.get("statusType") or task_args.get("statusTypes"))
    status_types_filter = [value.strip().lower() for value in status_types_filter if value.strip()]
    status_types_lookup = set(status_types_filter)

    async with http_client.session() as client:
        statuses_response = await client.get(statuses_url, headers=headers)

        try:
            statuses_payload = statuses_response.json()
        except Exception:
            statuses_payload = {}

        if isinstance(statuses_payload, dict):
            statuses_data = statuses_payload.get("data", []) or []
        else:
            statuses_data = []

    filtered_statuses = []
    for status in statuses_data:
        if not isinstance(status, dict):
            continue
        status_type = (status.get("status_type") or "").strip().lower()
        if status_types_lookup and status_type not in status_types_lookup:
            continue
        formatted = _format_status(status)
        if formatted:
            filtered_statuses.append(formatted)

    if statuses_response.status_code < 200 or statuses_response.status_code >= 300:
        return error_result(f"Statuses request failed: {statuses_response.status_code} {str(statuses_payload)}",)

    return ok_result({
        "statuses_count": len(filtered_statuses),
        "statuses": filtered_statuses,
        "filters": {
            "statusTypes": status_types_filter,
        },
    })


