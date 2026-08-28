from datetime import datetime, timezone

from src.core.models.request_context import RequestContext
from src.core.interfaces.http_client import HttpClient
from src.core.models.types import Header
from src.shared.normalize import clean_int, clean_text
from src.shared.result import ok_result, error_result

from src.shared.http import format_error, request_json


def _default_leave_range() -> tuple[str, str]:
    today = datetime.now(timezone.utc).date()
    end_of_next_year = today.replace(year=today.year + 1, month=12, day=31)
    return today.isoformat(), end_of_next_year.isoformat()


async def run(task_args, context: RequestContext, http_client: HttpClient):
    api_base_url = context.api_base_url
    headers = context.headers

    task_args = task_args if isinstance(task_args, dict) else {}
    status = task_args.get("status")
    mine = task_args.get("mine")
    if mine is None:
        mine = task_args.get("isMine")
    mine = bool(mine) if isinstance(mine, bool) else str(mine).strip().lower() in {"1", "true", "yes", "y", "on"}

    employee_id = task_args.get("employee_id") or task_args.get("employeeID")
    if not employee_id and mine:
        employee_id = context.request_headers.get(Header.X_EMPLOYEE_ID)

    from_date = clean_text(task_args.get("from_date") or task_args.get("fromDate"))
    to_date = clean_text(task_args.get("to_date") or task_args.get("toDate"))
    if not from_date or not to_date:
        default_from_date, default_to_date = _default_leave_range()
        if not from_date:
            from_date = default_from_date
        if not to_date:
            to_date = default_to_date
    recursive = task_args.get("recursive")
    if recursive is None:
        recursive = task_args.get("isRecursive")
    recursive = bool(recursive) if isinstance(recursive, bool) else str(recursive).strip().lower() in {"1", "true", "yes", "y", "on"}

    page = clean_int(task_args.get("page") or task_args.get("pageNumber"))
    size = clean_int(task_args.get("size") or task_args.get("pageSize"))
    if page is None:
        page = 0
    if size is None:
        size = 1000 if recursive else 20
    page = max(page, 0)
    size = min(max(size, 1), 1000)

    query_params = {
        "page": page,
        "size": size,
        "recursive": recursive,
        "mine": mine,
    }
    if status:
        if isinstance(status, list):
            statuses = [clean_text(s).upper() for s in status if clean_text(s)]
            if len(statuses) == 1:
                query_params["status.equals"] = statuses[0]
            elif len(statuses) > 1:
                query_params["status.in"] = statuses
        else:
            status_str = clean_text(status)
            if "," in status_str:
                statuses = [s.strip().upper() for s in status_str.split(",") if s.strip()]
                query_params["status.in"] = statuses
            else:
                query_params["status.equals"] = status_str.upper()
    if employee_id:
        query_params["employeeId.equals"] = employee_id
    if from_date:
        query_params["endDate.greaterThanOrEqual"] = f"{from_date}T00:00:00Z"
    if to_date:
        query_params["startDate.lessThanOrEqual"] = f"{to_date}T23:59:59Z"

    requests_url = f"{api_base_url}/v1/to/time-off-requests"

    all_requests = []
    final_meta = None
    final_status_code = 200
    pages_fetched = 0

    async with http_client.session() as client:
        current_page = page
        while True:
            current_params = {
                key: value for key, value in query_params.items() if key != "recursive"
            }
            current_params["page"] = current_page
            current_params["size"] = size
            try:
                status_code, payload = await request_json(client, "GET", requests_url, params=current_params, headers=headers)
            except Exception as exc:
                return error_result(str(format_error(exc=exc)),)

            final_status_code = status_code
            pages_fetched += 1
            if isinstance(payload, dict):
                requests = payload.get("data") or []
                meta = payload.get("meta")
            else:
                requests = []
                meta = None

            if status_code >= 400:
                return error_result(str(format_error(payload)),)

            if isinstance(requests, list):
                all_requests.extend(requests)

            final_meta = meta
            has_next = False
            if isinstance(meta, dict):
                has_next = bool(meta.get("has_next"))

            if not recursive or not has_next:
                break
            current_page += 1

    formatted_requests = []
    for request in all_requests:
        time_off_type = request.get("time_off_type") if isinstance(request, dict) else {}
        employee = request.get("employee") if isinstance(request, dict) else {}
        teams = []
        if isinstance(employee, dict):
            employee_teams = employee.get("teams")
            if isinstance(employee_teams, list):
                for team in employee_teams:
                    if not isinstance(team, dict):
                        continue
                    team_name = team.get("name")
                    if team_name:
                        teams.append({"name": team_name})
        formatted_requests.append({
            "request_id": request.get("id") if isinstance(request, dict) else None,
            "status": request.get("status") if isinstance(request, dict) else None,
            "start_date": request.get("start_date") if isinstance(request, dict) else None,
            "end_date": request.get("end_date") if isinstance(request, dict) else None,
            "time_off_type_id": time_off_type.get("id") if isinstance(time_off_type, dict) else None,
            "time_off_type_name": time_off_type.get("name") if isinstance(time_off_type, dict) else None,
            "employee": {
                "employee_name": employee.get("full_name") if isinstance(employee, dict) else None,
                "employee_email": employee.get("email") if isinstance(employee, dict) else None,
                "teams": teams,
            },
        })

    enriched_meta = final_meta if isinstance(final_meta, dict) else {}
    enriched_meta = {
        **enriched_meta,
        "pages_fetched": pages_fetched,
        "total_items_returned": len(formatted_requests),
    }

    return ok_result({
        "data": formatted_requests,
        "meta": enriched_meta,
        "query": query_params,
    })
