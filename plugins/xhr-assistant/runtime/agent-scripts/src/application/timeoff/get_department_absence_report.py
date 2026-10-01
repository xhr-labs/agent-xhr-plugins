from __future__ import annotations

from collections import defaultdict
from datetime import date, datetime, timezone
import re
from typing import Any

from src.core.interfaces.http_client import HttpClient
from src.core.models.request_context import RequestContext
from src.shared.http import format_error, request_json
from src.shared.normalize import clean_int, clean_text
from src.shared.result import error_result, ok_result


REPORT_PATH = "/v1/to/reports/time-off/summary"
ACTION_NAME = "render_stackedbarchart"
DEFAULT_STATUS = "APPROVED"
COLORS = (
    "#5B8DEF",
    "#68C3A3",
    "#F7B500",
    "#F45B69",
    "#9B8FE2",
    "#E887C8",
    "#5AA8D6",
)
VALID_STATUSES = {"PENDING", "APPROVED", "REJECTED", "CANCELLED"}
SNAKE_CASE_PART_PATTERN = re.compile(r"_([a-zA-Z0-9])")


def _report_period(task_args: dict[str, Any]) -> tuple[str, str] | None:
    start_date = clean_text(task_args.get("start_date") or task_args.get("startDate"))
    end_date = clean_text(task_args.get("end_date") or task_args.get("endDate"))
    if start_date or end_date:
        if not start_date or not end_date:
            return None
        try:
            start = date.fromisoformat(start_date)
            end = date.fromisoformat(end_date)
        except ValueError:
            return None
        if start > end:
            return None
        return start.isoformat(), end.isoformat()

    year = clean_int(task_args.get("year"))
    if year is None:
        year = datetime.now(timezone.utc).year - 1
    if year < 1900 or year > 9999:
        return None
    return f"{year}-01-01", f"{year}-12-31"


def _normalize_response_keys(value: Any) -> Any:
    if isinstance(value, list):
        return [_normalize_response_keys(item) for item in value]
    if not isinstance(value, dict):
        return value
    return {
        SNAKE_CASE_PART_PATTERN.sub(
            lambda match: match.group(1).upper(), str(key)
        ): _normalize_response_keys(item)
        for key, item in value.items()
    }


def _extract_detail_rows(payload: Any) -> list[dict[str, Any]]:
    data = payload.get("data") if isinstance(payload, dict) and "data" in payload else payload
    data = _normalize_response_keys(data)
    if not isinstance(data, dict):
        return []
    rows = data.get("detailRows")
    return [row for row in rows if isinstance(row, dict)] if isinstance(rows, list) else []


def _chart_content(
    rows: list[dict[str, Any]], status: str
) -> tuple[dict[str, Any], dict[str, Any]] | None:
    request_ids: dict[str, dict[str, set[str]]] = defaultdict(lambda: defaultdict(set))
    for row in rows:
        request_id = clean_text(row.get("requestId"))
        if not request_id:
            continue
        department = clean_text(row.get("departmentName")) or "Unassigned"
        leave_type = clean_text(row.get("timeOffTypeName")) or "Unspecified"
        request_ids[department][leave_type].add(request_id)

    if not request_ids:
        return None

    type_totals: dict[str, int] = defaultdict(int)
    for department_types in request_ids.values():
        for leave_type, ids in department_types.items():
            type_totals[leave_type] += len(ids)
    leave_types = sorted(type_totals, key=lambda name: (-type_totals[name], name))
    type_keys = {leave_type: f"type_{index + 1}" for index, leave_type in enumerate(leave_types)}

    ranked_departments = sorted(
        request_ids,
        key=lambda name: (-sum(len(ids) for ids in request_ids[name].values()), name),
    )
    chart_rows = []
    department_totals = []
    for department in ranked_departments:
        type_counts = request_ids[department]
        total = sum(len(ids) for ids in type_counts.values())
        chart_rows.append(
            {
                "department": department,
                **{
                    type_keys[leave_type]: len(type_counts.get(leave_type, set()))
                    for leave_type in leave_types
                },
            }
        )
        department_totals.append({"department": department, "requestCount": total})

    return (
        {
            "data": chart_rows,
            "series": [
                {
                    "dataKey": type_keys[leave_type],
                    "name": leave_type,
                    "color": COLORS[index % len(COLORS)],
                    "showLabel": True,
                }
                for index, leave_type in enumerate(leave_types)
            ],
            "xAxisKey": "department",
            "title": f"{status.capitalize()} absence requests by department and type",
            "showLegend": True,
        },
        {
            "topDepartment": department_totals[0]["department"],
            "topDepartmentRequestCount": department_totals[0]["requestCount"],
            "departmentTotals": department_totals,
        },
    )


def _assistant_message(summary: dict[str, Any], status: str, start_date: str, end_date: str) -> str:
    count = summary["topDepartmentRequestCount"]
    request_label = "request" if count == 1 else "requests"
    return (
        f"{summary['topDepartment']} had the most {status.lower()} absence "
        f"{request_label} from {start_date} to {end_date}: {count}."
    )


async def run(task_args, context: RequestContext, http_client: HttpClient):
    task_args = task_args if isinstance(task_args, dict) else {}
    period = _report_period(task_args)
    if period is None:
        return error_result(
            "provide a valid year or both start_date and end_date in YYYY-MM-DD format"
        )
    start_date, end_date = period

    status = (clean_text(task_args.get("status")) or DEFAULT_STATUS).upper()
    if status not in VALID_STATUSES:
        return error_result("status must be PENDING, APPROVED, REJECTED, or CANCELLED")

    query_params = {
        "fromDate": start_date,
        "toDate": end_date,
        "timeline": "RANGE",
        "groupBy": "DEPARTMENT",
        "status": status,
    }
    endpoint = f"{context.api_base_url}{REPORT_PATH}"
    try:
        async with http_client.session() as client:
            status_code, payload = await request_json(
                client, "GET", endpoint, params=query_params, headers=context.headers
            )
    except Exception as exc:
        return error_result(str(format_error(exc=exc)))

    if status_code >= 400:
        return error_result(str(format_error(payload)))

    chart = _chart_content(_extract_detail_rows(payload), status)
    if chart is None:
        return ok_result(
            {
                "startDate": start_date,
                "endDate": end_date,
                "status": status,
                "topDepartment": None,
                "topDepartmentRequestCount": 0,
                "departmentTotals": [],
            }
        )

    content, summary = chart
    return ok_result(
        {
            "action": ACTION_NAME,
            "content": content,
            "assistant_message": _assistant_message(
                summary, status, start_date, end_date
            ),
            "startDate": start_date,
            "endDate": end_date,
            "status": status,
            **summary,
        }
    )
