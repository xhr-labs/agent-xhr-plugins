from __future__ import annotations

from typing import Any

from src.application.allocation_management.dashboard_common import (
    aggregate_breakdown_rows,
    aggregate_rows,
    build_filters,
    fetch_dashboard_data,
    resolve_timeline_periods,
    with_month,
)
from src.application.allocation_management.dashboard_view import (
    allocation_by_line,
    chart_breakdown,
    metric_detail_rows,
    monthly_utilization,
    project_chart,
    status_chart,
    timesheet_view,
)
from src.core.interfaces.http_client import HttpClient
from src.core.models.request_context import RequestContext
from src.shared.http import FetchJsonError
from src.shared.result import error_result, ok_result


RESOURCE_REPORTS_PATH = "/v1/ralsm/reports/resources"


def _rows(data: dict[str, Any], key: str) -> list[dict[str, Any]]:
    value = data.get(key)
    return value if isinstance(value, list) else []


async def run(task_args, context: RequestContext, http_client: HttpClient):
    task_args = task_args if isinstance(task_args, dict) else {}
    try:
        period = resolve_timeline_periods(task_args)
    except ValueError as exc:
        return error_result(str(exc))

    filters = build_filters(task_args)
    base_url = f"{context.api_base_url}{RESOURCE_REPORTS_PATH}"
    summary_months = period["summaryMonths"]
    trend_months = period["trendMonths"]
    required_summary_months = list(dict.fromkeys(summary_months + trend_months))
    summary_by_month = {}
    employee_allocations = []

    try:
        async with http_client.session() as client:
            for report_month in required_summary_months:
                summary_by_month[report_month] = await fetch_dashboard_data(
                    client,
                    f"{base_url}/summary",
                    context.headers,
                    {"month": report_month, **filters},
                )

            for report_month in summary_months:
                allocation_detail = await fetch_dashboard_data(
                    client,
                    f"{base_url}/employee-allocations",
                    context.headers,
                    {"month": report_month, **filters},
                )
                employee_allocations.append(
                    {"month": report_month, "data": allocation_detail}
                )

            timesheet = await fetch_dashboard_data(
                client,
                f"{base_url}/timesheet",
                context.headers,
                {
                    "fromMonth": trend_months[0],
                    "toMonth": trend_months[-1],
                    **filters,
                },
            )
    except FetchJsonError as exc:
        return error_result(
            f"Allocation dashboard request failed: {exc.status_code} {exc}"
        )
    except ValueError as exc:
        return error_result(str(exc))
    except Exception as exc:
        return error_result(f"Allocation dashboard request failed: {exc}")

    chart_summaries = [
        {"month": month, "data": summary_by_month[month]}
        for month in summary_months
    ]
    trend_summaries = [
        {"month": month, "data": summary_by_month[month]}
        for month in trend_months
    ]
    metric_summary = summary_by_month[period["reportMonth"]]
    allocation_summary = metric_summary.get("allocationSummary") or {}

    def chart_rows(key):
        return [
            row
            for item in chart_summaries
            for row in _rows(item["data"], key)
        ]

    status_breakdowns = aggregate_breakdown_rows(
        chart_rows("allocationStatusBreakdowns")
    )
    project_type_breakdowns = aggregate_breakdown_rows(
        chart_rows("projectTypeAllocationBreakdowns")
    )
    department_breakdowns = aggregate_breakdown_rows(
        chart_rows("departmentUtilizationBreakdowns")
    )
    line_matrix = aggregate_rows(
        chart_rows("sourceLineAllocatedLineMatrix"),
        ("sourceLineKey", "allocatedLineKey", "lineType"),
        ("allocatedManMonths", "allocationPercentage"),
    )
    line_status_fields = (
        "plannedManMonths", "unverifiedManMonths", "tentativeManMonths",
        "totalManMonths", "plannedPercentage", "unverifiedPercentage",
        "tentativePercentage", "totalPercentage",
    )
    source_line_statuses = aggregate_rows(
        chart_rows("sourceLineStatusBreakdowns"), ("key",), line_status_fields
    )
    allocated_line_statuses = aggregate_rows(
        chart_rows("allocatedLineStatusBreakdowns"), ("key",), line_status_fields
    )
    employee_detail = aggregate_rows(
        chart_rows("employeeAllocationStatusRows"),
        ("employeeId", "sourceLineKey"),
        ("allocatedManMonths", "capacityManMonths", "timesheetManMonths"),
    )
    for row in employee_detail:
        capacity = row.get("capacityManMonths") or 0
        row["totalPercentage"] = (
            (row.get("allocatedManMonths") or 0) / capacity * 100
            if capacity > 0 else 0
        )

    project_rows = []
    employee_rows = []
    for item in employee_allocations:
        report_month = item["month"]
        detail = item["data"] if isinstance(item["data"], dict) else {}
        project_rows.extend(
            with_month(detail.get("projectAllocationLineRows"), report_month)
        )
        employee_rows.extend(
            with_month(detail.get("employeeAllocationLineRows"), report_month)
        )

    utilization_tables = monthly_utilization(trend_summaries)
    allocation_line_tables = allocation_by_line(
        allocated_line_statuses,
        source_line_statuses,
        line_matrix,
        project_rows,
    )
    timesheet_sections = timesheet_view(timesheet, trend_months)

    return ok_result({
        "period": {**period, "metricMonths": [period["reportMonth"]]},
        "filters": filters,
        "sections": {
            "metricCards": {
                "allocatedProjects": allocation_summary.get("allocatedProjectCount", 0),
                "totalAllocatedManMonths": allocation_summary.get("allocatedManMonths", 0),
                "internalResources": allocation_summary.get("ownLineResourceCount", 0),
                "borrowedResources": allocation_summary.get("crossLineResourceCount", 0),
            },
            "summary": {
                "allocationByProjectType": chart_breakdown(
                    project_type_breakdowns, "allocatedManMonths"
                ),
                "allocationByProjectStatus": status_chart(
                    status_breakdowns, "allocatedManMonths"
                ),
                "employeeCountByProjectStatus": status_chart(
                    status_breakdowns, "sourceFactCount"
                ),
                "allocationByProject": project_chart(project_rows),
                "utilizationTrend": [
                    {
                        "month": item["month"],
                        "utilizationRate": (
                            item["data"].get("allocationSummary") or {}
                        ).get("utilizationRate", 0),
                    }
                    for item in trend_summaries
                ],
                "utilizationByDepartment": chart_breakdown(
                    department_breakdowns, "utilizationRate"
                ),
            },
            "utilization": {
                "employeeDetail": metric_detail_rows(employee_detail),
                "departmentByMonth": utilization_tables["departmentRows"],
                "employeeByMonth": utilization_tables["employeeRows"],
                "totalByMonth": utilization_tables["totalByMonth"],
                "total": utilization_tables["total"],
            },
            "allocationByLine": {
                **allocation_line_tables,
                "employeeAllocationRows": employee_rows,
            },
            "timesheet": timesheet_sections,
        },
    })
