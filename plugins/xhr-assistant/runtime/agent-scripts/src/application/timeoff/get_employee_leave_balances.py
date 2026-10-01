from datetime import datetime, timezone
from src.core.models.request_context import RequestContext
from src.core.interfaces.http_client import HttpClient
from src.shared.normalize import clean_int, clean_text
from src.shared.result import ok_result, error_result
from src.shared.http import format_error, request_json


async def run(task_args, context: RequestContext, http_client: HttpClient):
    api_base_url = context.api_base_url
    headers = context.headers

    task_args = task_args if isinstance(task_args, dict) else {}
    employee_id = clean_text(task_args.get("employee_id") or task_args.get("employeeId"))
    year = clean_int(task_args.get("year")) or datetime.now(timezone.utc).year

    endpoint = f"{api_base_url}/v1/to/time-off-balances"
    query_params = {}
    if year:
        query_params["year.equals"] = year
    if employee_id:
        query_params["employeeId.equals"] = employee_id

    async with http_client.session() as client:
        try:
            status_code, payload = await request_json(client, "GET", endpoint, params=query_params, headers=headers)
        except Exception as exc:
            return error_result(str(format_error(exc=exc)))

    if status_code >= 400:
        return error_result(str(format_error(payload)))

    balances = payload.get("data") if isinstance(payload, dict) else payload
    if not isinstance(balances, list):
        balances = []

    formatted = []
    for b in balances:
        if not isinstance(b, dict):
            continue
        emp = b.get("employee") if isinstance(b.get("employee"), dict) else {}
        ttype = b.get("time_off_type") if isinstance(b.get("time_off_type"), dict) else {}
        formatted.append({
            "balance_id": b.get("id"),
            "employee_id": emp.get("id") or b.get("employee_id"),
            "employee_name": emp.get("full_name") or b.get("employee_name"),
            "time_off_type_id": ttype.get("id") or b.get("time_off_type_id"),
            "time_off_type_name": ttype.get("name") or b.get("time_off_type_name"),
            "available_days": b.get("available_days") or b.get("availableDays") or b.get("balance"),
            "used_days": b.get("used_days") or b.get("usedDays"),
            "pending_days": b.get("pending_days") or b.get("pendingDays"),
            "total_allowance": b.get("total_allowance") or b.get("totalAllowance"),
            "year": year,
        })

    return ok_result({
        "year": year,
        "balances_count": len(formatted),
        "balances": formatted,
        "query": query_params,
    })
