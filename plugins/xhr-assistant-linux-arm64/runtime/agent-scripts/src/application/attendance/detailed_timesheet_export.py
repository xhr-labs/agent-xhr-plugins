from __future__ import annotations

from typing import Any

from src.application.attendance import get_timesheet_requests
from src.application.attendance.attendance_reports_common import format_duration
from src.core.interfaces.http_client import HttpClient
from src.core.models.request_context import RequestContext
from src.shared.normalize import clean_text, normalize_list
from src.shared.result import error_result, ok_result


STATUS_VALUES = {"PENDING", "APPROVED", "REJECTED", "CANCELED"}


def _duration_to_minutes(value: Any) -> int:
    if isinstance(value, dict):
        try:
            return int(value.get("hours") or 0) * 60 + int(value.get("minutes") or 0)
        except Exception:
            return 0
    if isinstance(value, (int, float)):
        return int(value)
    return 0


def _expected_minutes(args: dict[str, Any]) -> int | None:
    expected_minutes = args.get("expectedMinutes") or args.get("expected_minutes")
    if expected_minutes is not None and str(expected_minutes).strip():
        try:
            return int(expected_minutes)
        except Exception:
            return None

    expected_hours = args.get("expectedHours") or args.get("expected_hours")
    if expected_hours is not None and str(expected_hours).strip():
        try:
            return int(float(str(expected_hours).strip()) * 60)
        except Exception:
            return None

    return None


def _looks_truncated(note: Any) -> bool:
    if not isinstance(note, str):
        return False
    text = note.strip()
    if not text:
        return False
    return text.endswith("...") or text.endswith("…")


def _format_row(item: dict[str, Any]) -> dict[str, Any]:
    worked_minutes = _duration_to_minutes(item.get("worked_hours"))
    return {
        "requestId": item.get("request_id"),
        "employeeId": item.get("employee_id"),
        "employeeName": item.get("employee_name"),
        "employeeEmail": item.get("employee_email"),
        "date": item.get("entry_date"),
        "from": item.get("start_time"),
        "to": item.get("end_time"),
        "workedHours": format_duration(worked_minutes),
        "workedMinutes": worked_minutes,
        "shiftName": item.get("shift_name"),
        "status": item.get("status"),
        "workMode": item.get("work_mode"),
        "scheduleType": item.get("schedule_type"),
        "isPublicHoliday": item.get("is_public_holiday"),
        "note": item.get("notes"),
        "noteLooksTruncated": _looks_truncated(item.get("notes")),
    }


async def run(task_args: Any, context: RequestContext, http_client: HttpClient) -> dict[str, Any]:
    args = task_args if isinstance(task_args, dict) else {}

    employee_id = clean_text(args.get("employeeId") or args.get("employee_id"))
    start_date = clean_text(args.get("startDate") or args.get("start_date"))
    end_date = clean_text(args.get("endDate") or args.get("end_date"))

    if not employee_id:
        return error_result(
            "employeeId is required. Resolve the employee first; do not run detailed export from a fuzzy name."
        )
    if not start_date or not end_date:
        return error_result("startDate and endDate are required for detailed timesheet export.")

    statuses = []
    for value in normalize_list(args.get("statuses")):
        upper = str(value).strip().upper()
        if upper in STATUS_VALUES:
            statuses.append(upper)
    if not statuses:
        statuses = ["PENDING"]

    sort_value = clean_text(args.get("sort")) or "entryDate,asc"
    expected = _expected_minutes(args)

    requests_payload = await get_timesheet_requests.run(
        {
            "employeeIds": [employee_id],
            "startDate": start_date,
            "endDate": end_date,
            "statuses": statuses,
            "recursive": True,
            "size": 1000,
            "sort": sort_value,
        },
        context,
        http_client,
    )

    if not requests_payload.get("ok"):
        return requests_payload

    data = requests_payload.get("data") or {}
    raw_requests = data.get("requests") or []
    matching_requests = []
    mismatched_requests = []

    for item in raw_requests:
        if not isinstance(item, dict):
            continue
        if item.get("employee_id") == employee_id:
            matching_requests.append(item)
        else:
            mismatched_requests.append(item)

    rows = [_format_row(item) for item in matching_requests]
    rows.sort(key=lambda row: (row.get("date") or "", row.get("from") or "", row.get("requestId") or ""))

    total_minutes = sum(row.get("workedMinutes") or 0 for row in rows)
    truncated_rows = [row for row in rows if row.get("noteLooksTruncated")]
    employee_names = sorted({row.get("employeeName") for row in rows if row.get("employeeName")})
    employee_emails = sorted({row.get("employeeEmail") for row in rows if row.get("employeeEmail")})
    meta = data.get("meta") or {}

    validation = {
        "identityMismatchCount": len(mismatched_requests),
        "excludedMismatchedRows": [
            {
                "requestId": item.get("request_id"),
                "employeeId": item.get("employee_id"),
                "employeeName": item.get("employee_name"),
                "employeeEmail": item.get("employee_email"),
                "date": item.get("entry_date"),
            }
            for item in mismatched_requests
        ],
        "hasNext": bool(meta.get("has_next")),
        "pagesFetched": meta.get("pages_fetched"),
        "pageSize": meta.get("page_size"),
        "returnedRowsBeforeIdentityFilter": len(raw_requests),
        "returnedRowsAfterIdentityFilter": len(rows),
        "totalWorkedMinutes": total_minutes,
        "totalWorkedHours": format_duration(total_minutes),
        "expectedMinutes": expected,
        "matchesExpectedMinutes": None if expected is None else total_minutes == expected,
        "truncatedNoteCount": len(truncated_rows),
        "truncatedNotes": [
            {
                "requestId": row.get("requestId"),
                "date": row.get("date"),
                "from": row.get("from"),
                "to": row.get("to"),
                "note": row.get("note"),
            }
            for row in truncated_rows
        ],
    }

    return ok_result(
        {
            "employeeVerification": {
                "employeeId": employee_id,
                "employeeNamesInRows": employee_names,
                "employeeEmailsInRows": employee_emails,
            },
            "selection": {
                "employeeId": employee_id,
                "startDate": start_date,
                "endDate": end_date,
                "statuses": statuses,
                "sort": sort_value,
            },
            "rowCount": len(rows),
            "rows": rows,
            "validation": validation,
            "source": {
                "endpoint": "/v1/atd/timesheets",
                "recursive": True,
                "officialExportFile": False,
            },
        }
    )
