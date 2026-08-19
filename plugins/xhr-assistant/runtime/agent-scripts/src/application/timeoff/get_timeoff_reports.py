from datetime import datetime, timezone
from src.core.models.request_context import RequestContext
from src.core.interfaces.http_client import HttpClient
from src.shared.normalize import clean_text
from src.shared.result import ok_result, error_result
from src.shared.http import format_error, request_json


async def run(task_args, context: RequestContext, http_client: HttpClient):
    api_base_url = context.api_base_url
    headers = context.headers

    task_args = task_args if isinstance(task_args, dict) else {}
    year = datetime.now(timezone.utc).year
    start_date = clean_text(task_args.get("start_date") or task_args.get("startDate") or task_args.get("from_date") or task_args.get("fromDate")) or f"{year}-01-01"
    end_date = clean_text(task_args.get("end_date") or task_args.get("endDate") or task_args.get("to_date") or task_args.get("toDate")) or f"{year}-12-31"

    query_params = {
        "fromDate": start_date,
        "toDate": end_date,
    }
    department_id = clean_text(task_args.get("department_id") or task_args.get("departmentId"))
    if department_id:
        query_params["departmentIds"] = department_id
    time_off_type_id = clean_text(task_args.get("time_off_type_id") or task_args.get("timeOffTypeId"))
    if time_off_type_id:
        query_params["timeOffTypeIds"] = time_off_type_id

    endpoint = f"{api_base_url}/v1/to/reports/time-off/summary"

    async with http_client.session() as client:
        try:
            status_code, payload = await request_json(client, "GET", endpoint, params=query_params, headers=headers)
        except Exception as exc:
            return error_result(str(format_error(exc=exc)))

    if status_code >= 400:
        return error_result(str(format_error(payload)))

    data = payload.get("data") if isinstance(payload, dict) and "data" in payload else payload

    return ok_result({
        "start_date": start_date,
        "end_date": end_date,
        "report": data,
        "query": query_params,
    })
