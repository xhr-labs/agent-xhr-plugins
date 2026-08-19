from datetime import datetime, timezone
from src.core.models.request_context import RequestContext
from src.core.interfaces.http_client import HttpClient
from src.shared.normalize import clean_text
from src.shared.result import ok_result, error_result
from src.shared.http import format_error, request_json


def _default_whos_out_range() -> tuple[str, str]:
    today = datetime.now(timezone.utc).date()
    today_str = today.isoformat()
    days_ahead = today.fromordinal(today.toordinal() + 30)
    return today_str, days_ahead.isoformat()


async def run(task_args, context: RequestContext, http_client: HttpClient):
    api_base_url = context.api_base_url
    headers = context.headers

    task_args = task_args if isinstance(task_args, dict) else {}
    from_date = clean_text(task_args.get("from_date") or task_args.get("fromDate") or task_args.get("start_date") or task_args.get("startDate"))
    to_date = clean_text(task_args.get("to_date") or task_args.get("toDate") or task_args.get("end_date") or task_args.get("endDate"))

    if not from_date or not to_date:
        def_from, def_to = _default_whos_out_range()
        if not from_date:
            from_date = def_from
        if not to_date:
            to_date = def_to

    department_id = clean_text(task_args.get("department_id") or task_args.get("departmentId"))
    employee_name = clean_text(task_args.get("employee_name") or task_args.get("employeeName") or task_args.get("search"))
    employee_id = clean_text(task_args.get("employee_id") or task_args.get("employeeId"))

    query_params = {
        "status.equals": "APPROVED",
        "sort": "startDate,asc",
        "size": 1000,
    }
    if from_date:
        query_params["endDate.greaterThanOrEqual"] = f"{from_date}T00:00:00Z"
    if to_date:
        query_params["startDate.lessThanOrEqual"] = f"{to_date}T23:59:59Z"
    if department_id:
        query_params["departmentId.in"] = department_id
    if employee_id:
        query_params["employeeId.in"] = employee_id
    if employee_name:
        query_params["employeeName.contains"] = employee_name

    endpoint = f"{api_base_url}/v1/to/time-off-requests"

    async with http_client.session() as client:
        try:
            status_code, payload = await request_json(client, "GET", endpoint, params=query_params, headers=headers)
        except Exception as exc:
            return error_result(str(format_error(exc=exc)))

    if status_code >= 400:
        return error_result(str(format_error(payload)))

    data = payload.get("data") if isinstance(payload, dict) else []
    if not isinstance(data, list):
        data = []

    whos_out_list = []
    for item in data:
        if not isinstance(item, dict):
            continue
        emp = item.get("employee") if isinstance(item.get("employee"), dict) else {}
        ttype = item.get("time_off_type") if isinstance(item.get("time_off_type"), dict) else {}
        whos_out_list.append({
            "request_id": item.get("id"),
            "employee_id": emp.get("id") or item.get("employee_id"),
            "employee_name": emp.get("full_name") or item.get("employee_name"),
            "employee_email": emp.get("email"),
            "time_off_type_id": ttype.get("id") or item.get("time_off_type_id"),
            "time_off_type_name": ttype.get("name") or item.get("time_off_type_name"),
            "start_date": item.get("start_date"),
            "end_date": item.get("end_date"),
            "days": item.get("days") or item.get("total_days"),
            "status": item.get("status"),
        })

    return ok_result({
        "whos_out_count": len(whos_out_list),
        "from_date": from_date,
        "to_date": to_date,
        "absences": whos_out_list,
        "query": query_params,
    })
