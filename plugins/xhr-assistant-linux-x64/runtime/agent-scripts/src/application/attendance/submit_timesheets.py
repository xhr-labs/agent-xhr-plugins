import json
from datetime import datetime, timedelta

from src.core.models.request_context import RequestContext
from src.core.interfaces.http_client import HttpClient
from src.shared.normalize import clean_text
from src.shared.result import ok_result, error_result
import src.application.attendance.get_timesheet_requests as get_timesheet_requests


def _to_int(value, default=0):
    try:
        return int(value)
    except Exception:
        return default


def _coerce_entries(task_args):
    if isinstance(task_args, dict):
        entries = task_args.get("entries")
        if isinstance(entries, list):
            return entries

        entries_json = task_args.get("entries_json") or task_args.get("entriesJson")
        if isinstance(entries_json, str) and entries_json.strip():
            try:
                parsed = json.loads(entries_json)
            except Exception:
                parsed = None
            if isinstance(parsed, list):
                return parsed

        return []
    if isinstance(task_args, list):
        return task_args
    return []


def _parse_date(value):
    if not value:
        return None
    try:
        v = value.strip() if isinstance(value, str) else value
        if isinstance(v, str) and v.endswith("Z"):
            v = v[:-1] + "+00:00"
        return datetime.fromisoformat(v).date()
    except Exception:
        return None


def _normalize_entries(entries):
    normalized = []
    missing_fields = []

    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            continue
        date = clean_text(entry.get("date"))
        start_time = clean_text(entry.get("start_time") or entry.get("startTime"))
        end_time = clean_text(entry.get("end_time") or entry.get("endTime"))
        if not date:
            missing_fields.append({"index": index, "field": "date"})
        if not start_time:
            missing_fields.append({"index": index, "field": "start_time"})
        if not end_time:
            missing_fields.append({"index": index, "field": "end_time"})
        if not date or not start_time or not end_time:
            continue
        normalized.append({
            "date": date,
            "start_time": start_time,
            "end_time": end_time,
            "break_duration_minutes": _to_int(entry.get("break_duration_minutes"), 0),
        })

    return normalized, missing_fields


def _resolve_date_bounds(entries):
    dates = [entry["date"] for entry in entries if entry.get("date")]
    if not dates:
        return None, None
    return min(dates), max(dates)


def _approved_leave_dates(approved_leaves):
    dates = set()
    for leave in approved_leaves:
        request_days = leave.get("request_days") or []
        if request_days:
            for day in request_days:
                d = _parse_date(day.get("request_date"))
                if d:
                    dates.add(d)
            continue
        start = _parse_date(leave.get("start_date"))
        end = _parse_date(leave.get("end_date"))
        if start and end:
            cur = start
            while cur <= end:
                dates.add(cur)
                cur += timedelta(days=1)
        elif start:
            dates.add(start)
    return dates


def _approved_timesheet_dates(approved_requests):
    dates = set()
    for request in approved_requests:
        if not isinstance(request, dict):
            continue
        d = _parse_date(request.get("entry_date"))
        if d:
            dates.add(d)
    return dates


async def run(task_args, context: RequestContext, http_client: HttpClient):
    api_base_url = context.api_base_url
    headers = context.headers

    task_args = task_args if isinstance(task_args, (dict, list)) else {}
    employee_id = clean_text(task_args.get("employee_id") if isinstance(task_args, dict) else None)
    entries = _coerce_entries(task_args)

    normalized_entries, entry_missing = _normalize_entries(entries)
    missing_fields = []
    if not employee_id:
        missing_fields.append("employee_id")
    if not normalized_entries:
        missing_fields.append("entries")

    if missing_fields or entry_missing:
        details = {
            "missingFields": missing_fields,
            "missingEntryFields": entry_missing,
        }
        return error_result(f"missing_required_fields: {json.dumps(details, ensure_ascii=False)}",)

    start_date, end_date = _resolve_date_bounds(normalized_entries)
    approved_leave_dates = set()
    approved_timesheet_dates = set()
    excluded_entries = []
    filtered_entries = list(normalized_entries)

    if start_date and end_date:
        start_dt = _parse_date(start_date)
        end_dt = _parse_date(end_date)
        if start_dt and end_dt:
            page_number = 0
            has_next = True
            approved_requests = []

            while has_next:
                approved_payload = await get_timesheet_requests.run({
                    "page": page_number,
                    "size": 1000,
                    "sort": "entryDate,desc",
                    "employee_ids": [employee_id],
                    "start_date": start_dt.isoformat(),
                    "end_date": end_dt.isoformat(),
                    "statuses": ["APPROVED", "PENDING"],
                }, context, http_client)

                if not isinstance(approved_payload, dict):
                    break

                if approved_payload.get("ok") is True:
                    approved_block = approved_payload.get("data") or {}
                    requests = approved_block.get("requests") or approved_block.get("data") or []
                    meta = approved_block.get("meta") or {}
                else:
                    requests = approved_payload.get("requests") or []
                    meta = approved_payload.get("meta") or {}
                if isinstance(requests, list):
                    approved_requests.extend(requests)
                if isinstance(meta, dict):
                    has_next = bool(meta.get("has_next"))
                else:
                    has_next = False

                page_number += 1

            approved_timesheet_dates = _approved_timesheet_dates(approved_requests)

            url = f"{api_base_url}/v1/to/time-off-requests"
            params = {
                "employeeId.equals": employee_id,
                "status.equals": "APPROVED",
                "startDate.lessThanOrEqual": f"{end_dt.isoformat()}T23:59:59Z",
                "endDate.greaterThanOrEqual": f"{start_dt.isoformat()}T00:00:00Z",
            }
            async with http_client.session() as client:
                leaves_response = await client.get(url, headers=headers, params=params)
                try:
                    leaves_payload = leaves_response.json()
                except Exception:
                    leaves_payload = {}
            approved_leaves = leaves_payload.get("data") if isinstance(leaves_payload, dict) else []
            approved_leave_dates = _approved_leave_dates(approved_leaves or [])

            filtered_entries = []
            for entry in normalized_entries:
                entry_date = _parse_date(entry.get("date"))
                if entry_date and entry_date in approved_leave_dates:
                    excluded_entries.append(entry)
                elif entry_date and entry_date in approved_timesheet_dates:
                    excluded_entries.append(entry)
                else:
                    filtered_entries.append(entry)

    if not filtered_entries:
        details = {
            "approvedLeaveDates": sorted(d.isoformat() for d in approved_leave_dates),
            "timesheetDates": sorted(d.isoformat() for d in approved_timesheet_dates),
            "excludedEntries": excluded_entries,
        }
        return error_result(f"entries_filtered_by_existing_timesheets_or_leave: {json.dumps(details, ensure_ascii=False)}",)

    start_date, end_date = _resolve_date_bounds(filtered_entries)
    payload = {
        "employee_id": employee_id,
        "start_date": start_date,
        "end_date": end_date,
        "entries": filtered_entries,
    }

    async with http_client.session() as client:
        response = await client.post(
            f"{api_base_url}/v1/atd/timesheets",
            json=payload,
            headers=headers,
        )
        try:
            response_payload = response.json()
        except Exception:
            response_payload = {}

    if response.status_code < 200 or response.status_code >= 300:
        return error_result(f"Submit timesheets failed: {response.status_code} {str(response_payload)}",)

    return ok_result({
        "data": response_payload.get("data") if isinstance(response_payload, dict) else None,
        "approvedLeaveDates": sorted(d.isoformat() for d in approved_leave_dates),
        "timesheetDates": sorted(d.isoformat() for d in approved_timesheet_dates),
        "excludedEntries": excluded_entries,
    })


