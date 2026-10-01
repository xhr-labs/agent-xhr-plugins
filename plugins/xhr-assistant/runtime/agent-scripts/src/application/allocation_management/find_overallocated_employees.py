from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from zoneinfo import ZoneInfo

from src.application.allocation_management.dashboard_common import (
    build_filters,
    fetch_dashboard_data,
    resolve_timeline_periods,
)
from src.core.interfaces.http_client import HttpClient
from src.core.models.request_context import RequestContext
from src.shared.http import FetchJsonError
from src.shared.result import error_result, ok_result


RESOURCE_REPORTS_PATH = "/v1/ralsm/reports/resources"


def _argument(task_args: dict[str, Any], key: str) -> Any:
    return task_args.get(key)


def _current_month(context: RequestContext) -> str:
    headers = {}
    headers.update(getattr(context, "request_headers", {}) or {})
    headers.update(getattr(context, "headers", {}) or {})
    timezone_name = next(
        (
            headers.get(key)
            for key in ("x-timezone", "X-Timezone", "timezone", "Timezone")
            if headers.get(key)
        ),
        None,
    )
    try:
        zone = ZoneInfo(str(timezone_name)) if timezone_name else timezone.utc
    except Exception:
        zone = timezone.utc
    return datetime.now(zone).strftime("%Y-%m")


def _resolve_period(task_args: dict[str, Any], context: RequestContext) -> dict[str, Any]:
    resolved_args = dict(task_args)
    if not str(_argument(resolved_args, "month") or "").strip():
        resolved_args["month"] = (
            _argument(resolved_args, "toMonth") or _current_month(context)
        )
    return resolve_timeline_periods(resolved_args)


def _number(value: Any) -> float:
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0.0


def _rows(data: dict[str, Any]) -> list[dict[str, Any]]:
    rows = data.get("employeeAllocationStatusRows")
    return rows if isinstance(rows, list) else []


def _aggregate_month(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    employees: dict[str, dict[str, Any]] = {}
    for row in rows:
        employee_id = str(row.get("employeeId") or "").strip()
        if not employee_id:
            continue
        target = employees.setdefault(
            employee_id,
            {
                "employeeId": employee_id,
                "employeeName": row.get("employeeName"),
                "departmentName": row.get("departmentName"),
                "allocatedManMonths": 0.0,
                "capacityManMonths": 0.0,
                "timesheetManMonths": 0.0,
                "sourceLines": set(),
            },
        )
        target["allocatedManMonths"] += _number(row.get("allocatedManMonths"))
        target["capacityManMonths"] = max(
            target["capacityManMonths"], _number(row.get("capacityManMonths"))
        )
        target["timesheetManMonths"] += _number(row.get("timesheetManMonths"))
        source_line = str(
            row.get("sourceLineLabel") or row.get("sourceLineKey") or ""
        ).strip()
        if source_line:
            target["sourceLines"].add(source_line)
    return employees


def _output_employee(employee: dict[str, Any], monthly: list[dict[str, Any]]) -> dict[str, Any]:
    allocated = employee["allocatedManMonths"]
    capacity = employee["capacityManMonths"]
    utilization = allocated / capacity * 100 if capacity > 0 else None
    return {
        "employeeId": employee["employeeId"],
        "employeeName": employee["employeeName"] or "Unknown employee",
        "departmentName": employee["departmentName"] or "Unassigned",
        "sourceLines": sorted(employee["sourceLines"]),
        "allocatedManMonths": round(allocated, 4),
        "capacityManMonths": round(capacity, 4),
        "utilizationRate": round(utilization, 2) if utilization is not None else None,
        "excessManMonths": round(max(allocated - capacity, 0), 4),
        "timesheetManMonths": round(employee["timesheetManMonths"], 4),
        "varianceManMonths": round(employee["timesheetManMonths"] - allocated, 4),
        "monthlyBreakdown": monthly,
    }


def _sort_key(employee: dict[str, Any]) -> tuple[float, float, str]:
    return (
        -(employee["utilizationRate"] or 0),
        -employee["excessManMonths"],
        str(employee["employeeName"]),
    )


async def run(task_args, context: RequestContext, http_client: HttpClient):
    task_args = task_args if isinstance(task_args, dict) else {}
    try:
        period = _resolve_period(task_args, context)
    except ValueError as exc:
        return error_result(str(exc))

    filters = build_filters(task_args)
    base_url = f"{context.api_base_url}{RESOURCE_REPORTS_PATH}"
    summaries: dict[str, dict[str, Any]] = {}
    try:
        async with http_client.session() as client:
            for month in period["summaryMonths"]:
                summaries[month] = await fetch_dashboard_data(
                    client,
                    f"{base_url}/summary",
                    context.headers,
                    {"month": month, **filters},
                )
    except FetchJsonError as exc:
        return error_result(
            f"Unable to load Allocation capacity data: {exc.status_code} {exc}"
        )
    except ValueError as exc:
        return error_result(str(exc))
    except Exception as exc:
        return error_result(f"Unable to load Allocation capacity data: {exc}")

    employees: dict[str, dict[str, Any]] = {}
    for month in period["summaryMonths"]:
        monthly_employees = _aggregate_month(_rows(summaries[month]))
        for employee_id, monthly_employee in monthly_employees.items():
            target = employees.setdefault(
                employee_id,
                {
                    "employeeId": employee_id,
                    "employeeName": monthly_employee["employeeName"],
                    "departmentName": monthly_employee["departmentName"],
                    "allocatedManMonths": 0.0,
                    "capacityManMonths": 0.0,
                    "timesheetManMonths": 0.0,
                    "sourceLines": set(),
                    "monthlyBreakdown": [],
                },
            )
            target["employeeName"] = target["employeeName"] or monthly_employee["employeeName"]
            target["departmentName"] = target["departmentName"] or monthly_employee["departmentName"]
            target["allocatedManMonths"] += monthly_employee["allocatedManMonths"]
            target["capacityManMonths"] += monthly_employee["capacityManMonths"]
            target["timesheetManMonths"] += monthly_employee["timesheetManMonths"]
            target["sourceLines"].update(monthly_employee["sourceLines"])
            month_allocated = monthly_employee["allocatedManMonths"]
            month_capacity = monthly_employee["capacityManMonths"]
            target["monthlyBreakdown"].append({
                "month": month,
                "allocatedManMonths": round(month_allocated, 4),
                "capacityManMonths": round(month_capacity, 4),
                "utilizationRate": (
                    round(month_allocated / month_capacity * 100, 2)
                    if month_capacity > 0 else None
                ),
            })

    overallocated = []
    zero_capacity = []
    for employee in employees.values():
        output = _output_employee(employee, employee["monthlyBreakdown"])
        if employee["capacityManMonths"] <= 0:
            zero_capacity.append(output)
        elif employee["allocatedManMonths"] > employee["capacityManMonths"]:
            overallocated.append(output)

    overallocated.sort(key=_sort_key)
    zero_capacity.sort(key=lambda employee: (-employee["allocatedManMonths"], employee["employeeName"]))
    return ok_result({
        "status": "READY",
        "period": period,
        "filters": filters,
        "thresholdPercent": 100,
        "evaluatedEmployeeCount": len(employees),
        "overallocatedEmployees": overallocated,
        "zeroCapacityEmployees": zero_capacity,
        "summary": {
            "overallocatedCount": len(overallocated),
            "zeroCapacityCount": len(zero_capacity),
            "totalEvaluatedEmployees": len(employees),
            "totalAllocatedManMonths": round(
                sum(employee["allocatedManMonths"] for employee in employees.values()), 4
            ),
            "totalCapacityManMonths": round(
                sum(employee["capacityManMonths"] for employee in employees.values()), 4
            ),
        },
    })
