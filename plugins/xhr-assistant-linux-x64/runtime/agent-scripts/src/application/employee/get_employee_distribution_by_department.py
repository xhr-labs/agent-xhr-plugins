from __future__ import annotations

from datetime import datetime, timezone
from math import isfinite
from typing import Any

from src.application.employee.employee_management_dashboard_common import (
    MONTH_PATTERN,
    normalize_response_keys,
)
from src.application.employee.employee_management_dashboard_view import display_rows
from src.core.interfaces.http_client import HttpClient
from src.core.models.request_context import RequestContext
from src.shared.http import format_error, request_json
from src.shared.normalize import clean_text
from src.shared.result import error_result, ok_result


REPORT_PATH = "/v1/em/reports/workforce/monthly-summary"
ACTION_NAME = "render_piechart"
COLORS = (
    "#5B8DEF",
    "#68C3A3",
    "#F7B500",
    "#F45B69",
    "#9B8FE2",
)


def _as_number(value: Any) -> int | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    if isinstance(value, float) and not isfinite(value):
        return None
    if value < 0:
        return None
    return int(value)


async def run(task_args, context: RequestContext, http_client: HttpClient):
    task_args = task_args if isinstance(task_args, dict) else {}
    month = clean_text(task_args.get("month")) or datetime.now(
        timezone.utc
    ).strftime("%Y-%m")
    if not MONTH_PATTERN.fullmatch(month):
        return error_result("month must be in YYYY-MM format")
    scope = (
        clean_text(
            task_args.get("headcount_scope") or task_args.get("headcountScope")
        )
        or "ACTIVE"
    ).upper()
    if scope not in {"ACTIVE", "TOTAL"}:
        return error_result("headcount_scope must be ACTIVE or TOTAL")

    endpoint = f"{context.api_base_url}{REPORT_PATH}"
    try:
        async with http_client.session() as client:
            status_code, payload = await request_json(
                client,
                "GET",
                endpoint,
                params={"month": month},
                headers=context.headers,
            )
    except Exception as exc:
        return error_result(str(format_error(exc=exc)))

    if status_code >= 400:
        return error_result(str(format_error(payload)))

    report = payload.get("data") if isinstance(payload, dict) else None
    report = normalize_response_keys(report)
    if not isinstance(report, dict):
        return error_result("Workforce report response is empty")

    summary = report.get("summary")
    summary = summary if isinstance(summary, dict) else {}
    raw_rows = report.get("departmentBreakdowns")
    rows = display_rows(
        [row for row in raw_rows if isinstance(row, dict)]
        if isinstance(raw_rows, list)
        else []
    )
    count_key = "activeHeadcount" if scope == "ACTIVE" else "totalHeadcount"
    chart_data = []
    for index, row in enumerate(rows):
        value = _as_number(row.get(count_key))
        if value is None or value == 0:
            continue
        label = clean_text(row.get("label")) or "Unassigned"
        chart_data.append(
            {
                "name": label,
                "value": value,
                "color": COLORS[index % len(COLORS)],
            }
        )

    total = _as_number(summary.get(count_key))
    if total is None:
        total = sum(item["value"] for item in chart_data)

    return ok_result(
        {
            "action": ACTION_NAME,
            "content": {
                "data": chart_data,
                "height": 300,
                "legendAlign": "start",
                "legendPosition": "right",
                "showLegend": True,
                "showLegendValues": True,
                "showLegendPercentages": True,
                "month": month,
                "headcountScope": scope,
                "total": total,
            },
        }
    )
