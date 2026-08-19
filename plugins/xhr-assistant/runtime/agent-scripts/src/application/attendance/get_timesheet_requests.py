import json
from datetime import datetime, timedelta, timezone

from src.core.models.request_context import RequestContext
from src.core.interfaces.http_client import HttpClient
from src.core.models.types import Header
from src.shared.normalize import clean_text, normalize_list, to_bool
from src.shared.result import ok_result, error_result

STATUS_VALUES = {"PENDING", "APPROVED", "REJECTED", "CANCELED"}


def _default_timesheet_date_range() -> tuple[str, str]:
    today = datetime.now(timezone.utc).date()
    first_day_this_month = today.replace(day=1)
    last_three_month_anchor = first_day_this_month - timedelta(days=1)
    for _ in range(2):
        last_three_month_anchor = last_three_month_anchor.replace(day=1) - timedelta(days=1)
    start_date = last_three_month_anchor.replace(day=1)
    return start_date.isoformat(), today.isoformat()


def _to_int(value, default):
    try:
        return int(value)
    except Exception:
        return default


def _format_request(item):
    if not isinstance(item, dict):
        return None
    employee = item.get("employee") or {}
    shift = item.get("shift") or {}
    return {
        "request_id": item.get("id"),
        "employee_id": employee.get("id"),
        "employee_name": employee.get("name"),
        "employee_email": employee.get("email"),
        "entry_date": item.get("entry_date"),
        "start_time": item.get("start_time"),
        "end_time": item.get("end_time"),
        "break_duration_minutes": item.get("break_duration_minutes"),
        "worked_hours": item.get("worked_hours"),
        "shift_id": shift.get("id"),
        "shift_name": shift.get("name"),
        "is_public_holiday": item.get("is_public_holiday"),
        "work_mode": item.get("work_mode"),
        "schedule_type": item.get("schedule_type"),
        "status": item.get("status"),
        "notes": item.get("notes"),
        "reject_reason": item.get("reject_reason"),
    }


def _resolve_has_next(meta, page_number, page_size, data_len):
    if isinstance(meta, dict):
        if "has_next" in meta:
            return bool(meta.get("has_next"))
        if "hasNext" in meta:
            return bool(meta.get("hasNext"))

        total_elements = meta.get("total_elements") or meta.get("totalElements") or meta.get("total")
        if total_elements is not None:
            try:
                total_elements = int(total_elements)
                return (page_number + 1) * page_size < total_elements
            except Exception:
                pass

        total_pages = meta.get("total_pages") or meta.get("totalPages")
        if total_pages is not None:
            try:
                total_pages = int(total_pages)
                return page_number + 1 < total_pages
            except Exception:
                pass

    return data_len >= page_size


async def run(task_args, context: RequestContext, http_client: HttpClient):
    api_base_url = context.api_base_url
    headers = context.headers

    args = task_args if isinstance(task_args, dict) else {}

    recursive = args.get("recursive")
    if recursive is None:
        recursive = args.get("isRecursive")
    recursive = to_bool(recursive)

    mine = args.get("mine")
    if mine is None:
        mine = args.get("isMine")
    mine = to_bool(mine)

    page_number = _to_int(args.get("page"), 0)
    page_size = _to_int(args.get("size"), 1000 if recursive else 20)
    sort_value = clean_text(args.get("sort")) or "entryDate,desc"

    page_number = max(page_number, 0)
    page_size = min(max(page_size, 1), 1000)

    employee_ids = normalize_list(args.get("employeeIds"))
    if mine and not employee_ids:
        employee_ids = normalize_list(context.request_headers.get(Header.X_EMPLOYEE_ID))

    start_date = clean_text(args.get("startDate"))
    end_date = clean_text(args.get("endDate"))
    if not start_date or not end_date:
        default_start_date, default_end_date = _default_timesheet_date_range()
        if not start_date:
            start_date = default_start_date
        if not end_date:
            end_date = default_end_date

    statuses = []
    for value in normalize_list(args.get("statuses")):
        upper = value.upper()
        if upper in STATUS_VALUES:
            statuses.append(upper)

    url = f"{api_base_url}/v1/atd/timesheets"

    all_requests = []
    final_status = 200
    pages_fetched = 0
    current_page_number = page_number
    last_has_next = False

    async with http_client.session() as client:
        while True:
            params = {
                "page": current_page_number,
                "size": page_size,
                "sort": sort_value,
            }

            if employee_ids:
                params["employeeIds"] = ",".join(employee_ids)
            if start_date:
                params["startDate"] = start_date
            if end_date:
                params["endDate"] = end_date
            if statuses:
                params["statuses"] = ",".join(statuses)

            response = await client.get(url, headers=headers, params=params)
            pages_fetched += 1
            final_status = response.status_code

            try:
                payload = response.json()
            except Exception:
                payload = {}

            if isinstance(payload, dict):
                requests = payload.get("data", []) or []
                meta = payload.get("meta")
            else:
                requests = []
                meta = None

            formatted_requests = []
            for item in requests:
                formatted = _format_request(item)
                if formatted:
                    formatted_requests.append(formatted)

            all_requests.extend(formatted_requests)
            last_has_next = _resolve_has_next(meta, current_page_number, page_size, len(formatted_requests))

            if response.status_code >= 400 or not recursive or not last_has_next:
                break
            current_page_number += 1

    output_meta = {
        "page_number": page_number,
        "page_size": page_size,
        "has_next": last_has_next,
        "pages_fetched": pages_fetched,
        "total_items_returned": len(all_requests),
    }

    if final_status < 200 or final_status >= 300:
        return error_result(f"Get timesheet requests failed: {final_status}",)

    return ok_result({
        "requests_count": len(all_requests),
        "requests": all_requests,
        "meta": output_meta,
        "filters": {
            "page": page_number,
            "size": page_size,
            "sort": sort_value,
            "employeeIds": employee_ids,
            "startDate": start_date,
            "endDate": end_date,
            "statuses": statuses,
            "mine": mine,
            "recursive": recursive,
        },
    })
