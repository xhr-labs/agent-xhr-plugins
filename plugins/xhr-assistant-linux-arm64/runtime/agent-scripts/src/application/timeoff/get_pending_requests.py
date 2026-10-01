from src.core.models.request_context import RequestContext
from src.core.interfaces.http_client import HttpClient
from src.shared.normalize import clean_int, clean_text
from src.shared.result import ok_result, error_result
from src.shared.http import format_error, request_json


async def run(task_args, context: RequestContext, http_client: HttpClient):
    api_base_url = context.api_base_url
    headers = context.headers

    task_args = task_args if isinstance(task_args, dict) else {}
    page = clean_int(task_args.get("page") or task_args.get("page_number") or task_args.get("pageNumber")) or 0
    size = clean_int(task_args.get("size") or task_args.get("page_size") or task_args.get("pageSize")) or 50

    department_id = clean_text(task_args.get("department_id") or task_args.get("departmentId"))
    employee_name = clean_text(task_args.get("employee_name") or task_args.get("employeeName") or task_args.get("search"))

    endpoint = f"{api_base_url}/v1/to/time-off-requests"
    query_params = {
        "status.equals": "PENDING",
        "sort": "createdAt,desc",
        "page": page,
        "size": size,
    }
    if department_id:
        query_params["departmentId.in"] = department_id
    if employee_name:
        query_params["employeeName.contains"] = employee_name

    async with http_client.session() as client:
        try:
            status_code, payload = await request_json(client, "GET", endpoint, params=query_params, headers=headers)
        except Exception as exc:
            return error_result(str(format_error(exc=exc)))

    if status_code >= 400:
        return error_result(str(format_error(payload)))

    requests = payload.get("data") if isinstance(payload, dict) else []
    if not isinstance(requests, list):
        requests = []

    pending_list = []
    for r in requests:
        if not isinstance(r, dict):
            continue
        emp = r.get("employee") if isinstance(r.get("employee"), dict) else {}
        ttype = r.get("time_off_type") if isinstance(r.get("time_off_type"), dict) else {}
        pending_list.append({
            "request_id": r.get("id"),
            "employee_id": emp.get("id") or r.get("employee_id"),
            "employee_name": emp.get("full_name") or r.get("employee_name"),
            "employee_email": emp.get("email"),
            "time_off_type_id": ttype.get("id") or r.get("time_off_type_id"),
            "time_off_type_name": ttype.get("name") or r.get("time_off_type_name"),
            "start_date": r.get("start_date"),
            "end_date": r.get("end_date"),
            "days": r.get("days") or r.get("total_days"),
            "reason": r.get("reason") or r.get("notes"),
            "created_at": r.get("created_at") or r.get("createdAt"),
            "status": "PENDING",
        })

    return ok_result({
        "pending_count": len(pending_list),
        "requests": pending_list,
        "query": query_params,
    })
