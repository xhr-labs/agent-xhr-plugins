from __future__ import annotations

from typing import Any

from src.application.attendance.attendance_reports_common import (
    fetch_timesheet_reports_api,
    fetch_timesheet_summary_api,
    resolve_report_period,
)
from src.application.attendance.attendance_reports_view import (
    calculate_kpi_summary,
    format_annual_report_rows,
    format_employee_detail_summary,
    format_period_report_rows,
)
from src.core.interfaces.http_client import HttpClient
from src.core.models.request_context import RequestContext
from src.shared.http import FetchJsonError
from src.shared.result import error_result, ok_result


REPORT_PATH = "/v1/atd/timesheets/report"
ANNUAL_REPORT_PATH = "/v1/atd/timesheets/annual-report"
SUMMARY_PATH = "/v1/atd/timesheets/summary"


async def run(task_args: Any, context: RequestContext, http_client: HttpClient) -> dict[str, Any]:
    task_args = task_args if isinstance(task_args, dict) else {}

    try:
        period = resolve_report_period(task_args)
    except ValueError as exc:
        return error_result(str(exc))

    mode = period["mode"]
    status = period["status"]
    department_id = task_args.get("departmentId") or task_args.get("department_id")
    search_name = task_args.get("searchName") or task_args.get("search_name")
    employee_id = task_args.get("employeeId") or task_args.get("employee_id")

    filters: dict[str, Any] = {}
    if department_id and str(department_id).strip():
        filters["department_id"] = str(department_id).strip()
    if search_name and str(search_name).strip():
        filters["search_name"] = str(search_name).strip()

    section_errors: dict[str, str] = {}
    reports_raw: list[dict[str, Any]] = []
    employee_detail_raw: dict[str, Any] | None = None

    try:
        async with http_client.session() as client:
            if mode == "annual":
                url = f"{context.api_base_url}{ANNUAL_REPORT_PATH}"
                params = {
                    "year": period["year"],
                    **filters,
                }
                reports_raw = await fetch_timesheet_reports_api(
                    client, url, context.headers, params
                )
            else:
                url = f"{context.api_base_url}{REPORT_PATH}"
                params = {
                    "start_date": period["startDate"],
                    "end_date": period["endDate"],
                    "status": status,
                    **filters,
                }
                reports_raw = await fetch_timesheet_reports_api(
                    client, url, context.headers, params
                )

            if employee_id and str(employee_id).strip():
                emp_url = f"{context.api_base_url}{SUMMARY_PATH}"
                emp_params = {
                    "employee_id": str(employee_id).strip(),
                    "start_date": period["startDate"],
                    "end_date": period["endDate"],
                    "statuses": status,
                }
                try:
                    employee_detail_raw = await fetch_timesheet_summary_api(
                        client, emp_url, context.headers, emp_params
                    )
                except Exception as exc:
                    section_errors["employeeDetail"] = f"Failed to fetch employee summary: {exc}"

    except FetchJsonError as exc:
        return error_result(f"Attendance reports request failed: {exc.status_code} {exc}")
    except Exception as exc:
        return error_result(f"Attendance reports request failed: {exc}")

    if mode == "annual":
        formatted_rows = format_annual_report_rows(reports_raw)
    else:
        formatted_rows = format_period_report_rows(reports_raw, status)

    kpi_summary = calculate_kpi_summary(formatted_rows, mode, status)

    result_data: dict[str, Any] = {
        "selection": {
            **period,
            **({"departmentId": filters["department_id"]} if "department_id" in filters else {}),
            **({"searchName": filters["search_name"]} if "search_name" in filters else {}),
            **({"employeeId": str(employee_id).strip()} if employee_id and str(employee_id).strip() else {}),
        },
        "kpiSummary": kpi_summary,
        "reports": formatted_rows,
        "sectionErrors": section_errors,
    }

    if employee_detail_raw:
        result_data["employeeDetail"] = format_employee_detail_summary(
            employee_detail_raw, status
        )

    return ok_result(result_data)
