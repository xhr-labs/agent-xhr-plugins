from __future__ import annotations

from typing import Any

from src.application.employee.employee_management_dashboard_common import (
    fetch_summary_batch,
    report_request_key,
    require_month,
    timeline_months,
)
from src.application.employee.employee_management_dashboard_view import (
    change_rows,
    display_rows,
    filter_options,
    offboarded_rows,
    stacked_department_employee_type,
    structure_items,
)
from src.core.interfaces.http_client import HttpClient
from src.core.models.request_context import RequestContext
from src.shared.result import error_result, ok_result


REPORT_PATH = "/v1/em/reports/workforce/monthly-summary"


def _empty_sections() -> dict[str, Any]:
    return {
        "timeline": [],
        "structure": {
            "byOrganization": [],
            "byEmployeeType": [],
            "byWorkLocation": [],
            "byJobTitle": [],
            "byJobTitleType": [],
        },
        "changeTables": {"departmentChanges": [], "employeeTypeChanges": []},
        "changeCharts": {
            "jobTitleTypeMovement": [],
            "monthlyOffboarding": {
                "month": None,
                "totalOffboarded": 0,
                "byOrganization": [],
            },
        },
        "employeeTypeByDepartment": {"data": [], "series": []},
    }


async def run(task_args, context: RequestContext, http_client: HttpClient):
    task_args = task_args if isinstance(task_args, dict) else {}
    try:
        month = require_month(task_args)
    except ValueError as exc:
        return error_result(str(exc))

    filters = {
        key: str(task_args[key]).strip()
        for key in ("departmentId", "employeeTypeId")
        if task_args.get(key) is not None and str(task_args[key]).strip()
    }
    months = timeline_months(month)
    url = f"{context.api_base_url}{REPORT_PATH}"

    option_params = {"month": month}
    timeline_params = [{"month": report_month, **filters} for report_month in months]
    section_errors = {}

    try:
        async with http_client.session() as client:
            reports = await fetch_summary_batch(
                client, url, context.headers, [option_params, *timeline_params]
            )
            option_result = reports[report_request_key(option_params)]
            option_summary = option_result["data"] or {}
            if option_result["error"]:
                section_errors["filterOptions"] = option_result["error"]

            summary_results = [
                reports[report_request_key(params)] for params in timeline_params
            ]
            current_result = summary_results[-1]
            current = current_result["data"] or {}
            if current_result["error"]:
                section_errors["currentMonth"] = current_result["error"]

            departments = [
                row for row in display_rows(current.get("departmentBreakdowns"))
                if row.get("id") and (row.get("activeHeadcount") or 0) > 0
            ][:8]
            department_params = []
            for department in departments:
                params = {"month": month, "departmentId": department["id"]}
                if filters.get("employeeTypeId"):
                    params["employeeTypeId"] = filters["employeeTypeId"]
                department_params.append(params)
            department_reports = await fetch_summary_batch(
                client, url, context.headers, department_params
            )
            department_results = [
                department_reports[report_request_key(params)]
                for params in department_params
            ]
            department_summaries = [
                result["data"] or {} for result in department_results
            ]
            if any(result["error"] for result in department_results):
                section_errors["employeeTypeByDepartment"] = (
                    "Some department data could not be loaded"
                )
    except Exception:
        return error_result("Employee management dashboard request failed")

    summary = current.get("summary") or {}
    sections = _empty_sections()
    sections["timeline"] = [
        {
            "month": report_month,
            "totalHeadcount": (
                (result["data"] or {}).get("summary") or {}
            ).get("totalHeadcount"),
            "newHiresCount": (
                (result["data"] or {}).get("summary") or {}
            ).get("newHiresCount"),
            "offboardedCount": (
                (result["data"] or {}).get("summary") or {}
            ).get("offboardedCount"),
            "status": "error" if result["error"] else "ready",
        }
        for report_month, result in zip(months, summary_results)
    ]
    if any(result["error"] for result in summary_results):
        section_errors["timeline"] = "Some monthly data could not be loaded"

    if current:
        sections.update(
            {
                "structure": {
                    "byOrganization": structure_items(
                        current.get("departmentBreakdowns")
                    ),
                    "byEmployeeType": structure_items(
                        current.get("employeeTypeBreakdowns")
                    ),
                    "byWorkLocation": structure_items(
                        current.get("workLocationBreakdowns")
                    ),
                    "byJobTitle": structure_items(
                        current.get("jobTitleBreakdowns")
                    ),
                    "byJobTitleType": structure_items(
                        current.get("jobTitleTypeBreakdowns")
                    ),
                },
                "changeTables": {
                    "departmentChanges": change_rows(
                        current.get("departmentBreakdowns"), 5
                    ),
                    "employeeTypeChanges": change_rows(
                        current.get("employeeTypeBreakdowns"), 5
                    ),
                },
                "changeCharts": {
                    "jobTitleTypeMovement": change_rows(
                        current.get("jobTitleTypeBreakdowns"), 8
                    ),
                    "monthlyOffboarding": {
                        "month": month,
                        "totalOffboarded": summary.get("offboardedCount", 0),
                        "byOrganization": offboarded_rows(
                            current.get("departmentBreakdowns")
                        ),
                    },
                },
                "employeeTypeByDepartment": stacked_department_employee_type(
                    departments,
                    current.get("employeeTypeBreakdowns") or [],
                    department_summaries,
                ),
            }
        )

    return ok_result({
        "selection": {"month": month, **filters},
        "filterOptions": {
            "departments": filter_options(option_summary.get("departmentBreakdowns")),
            "employeeTypes": filter_options(option_summary.get("employeeTypeBreakdowns")),
        },
        "sectionErrors": section_errors,
        "sections": sections,
    })
