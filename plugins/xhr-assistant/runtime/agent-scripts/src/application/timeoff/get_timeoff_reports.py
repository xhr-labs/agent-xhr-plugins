from datetime import date, datetime, timezone
from src.core.models.request_context import RequestContext
from src.core.interfaces.http_client import HttpClient
from src.shared.normalize import clean_text
from src.shared.result import ok_result, error_result
from src.shared.http import format_error, request_json


VALID_TIMELINES = {"DAY", "WEEK", "MONTH", "YEAR", "RANGE"}
VALID_GROUPS = {"EMPLOYEE", "DEPARTMENT", "COMPANY"}
VALID_STATUSES = {"PENDING", "APPROVED", "REJECTED", "CANCELLED"}


def _is_valid_date(value: str) -> bool:
    try:
        date.fromisoformat(value)
    except ValueError:
        return False
    return True


async def run(task_args, context: RequestContext, http_client: HttpClient):
    api_base_url = context.api_base_url
    headers = context.headers

    task_args = task_args if isinstance(task_args, dict) else {}
    year = datetime.now(timezone.utc).year
    start_date = clean_text(task_args.get("start_date") or task_args.get("startDate") or task_args.get("from_date") or task_args.get("fromDate")) or f"{year}-01-01"
    end_date = clean_text(task_args.get("end_date") or task_args.get("endDate") or task_args.get("to_date") or task_args.get("toDate")) or f"{year}-12-31"
    if not _is_valid_date(start_date) or not _is_valid_date(end_date):
        return error_result("start_date and end_date must be in YYYY-MM-DD format")
    if start_date > end_date:
        return error_result("start_date must be on or before end_date")

    query_params = {
        "fromDate": start_date,
        "toDate": end_date,
    }
    timeline = clean_text(task_args.get("timeline"))
    if timeline:
        timeline = timeline.upper()
        if timeline not in VALID_TIMELINES:
            return error_result("timeline must be DAY, WEEK, MONTH, YEAR, or RANGE")
        query_params["timeline"] = timeline
    group_by = clean_text(task_args.get("group_by") or task_args.get("groupBy"))
    if group_by:
        group_by = group_by.upper()
        if group_by not in VALID_GROUPS:
            return error_result("group_by must be EMPLOYEE, DEPARTMENT, or COMPANY")
        query_params["groupBy"] = group_by
    department_id = clean_text(task_args.get("department_id") or task_args.get("departmentId"))
    if department_id:
        query_params["departmentId"] = department_id
    time_off_type_id = clean_text(task_args.get("time_off_type_id") or task_args.get("timeOffTypeId"))
    if time_off_type_id:
        query_params["timeOffTypeId"] = time_off_type_id
    status = clean_text(task_args.get("status"))
    if status:
        status = status.upper()
        if status not in VALID_STATUSES:
            return error_result("status must be PENDING, APPROVED, REJECTED, or CANCELLED")
        query_params["status"] = status

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
