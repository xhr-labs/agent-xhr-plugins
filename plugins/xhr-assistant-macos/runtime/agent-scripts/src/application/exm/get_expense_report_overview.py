"""Read the Expense Management report overview: per-employee expense totals by currency."""

from __future__ import annotations

from src.application.exm.common import (
    as_args,
    base_url,
    call_json,
    date_range,
    list_result,
    optional_uuid,
    paging,
    require_enum,
    value,
)
from src.application.exm.common import EXPENSE_STATUSES
from src.core.interfaces.http_client import HttpClient
from src.core.models.request_context import RequestContext


VIEWS = ("overview", "export_candidates")


async def run(task_args, context: RequestContext, http_client: HttpClient):
    args = as_args(task_args)

    raw_view = value(args, "view")
    if isinstance(raw_view, str):
        raw_view = raw_view.replace("-", "_")
    view, error = require_enum(raw_view, "view", VIEWS)
    if error:
        return error
    view = view or "overview"

    date_from, date_to, error = date_range(args)
    if error:
        return error

    status, error = require_enum(value(args, "status"), "status", EXPENSE_STATUSES)
    if error:
        return error

    employee_id, error = optional_uuid(
        value(args, "employee_id", "employeeId"),
        "employee_id",
        lookup_hint="skills/employee/search_employees",
    )
    if error:
        return error

    department_id, error = optional_uuid(
        value(args, "department_id", "departmentId"),
        "department_id",
        lookup_hint="skills/company (department lookup)",
    )
    if error:
        return error

    params = paging(args)
    if employee_id:
        params["employeeId"] = employee_id
    if department_id:
        params["departmentId"] = department_id
    if date_from:
        params["dateFrom"] = date_from
    if date_to:
        params["dateTo"] = date_to
    if status:
        params["status"] = status

    # ``export_candidates`` returns the flat per-expense rows the app's CSV export is
    # built from. It is the same filter surface, so it stays on this leaf instead of
    # adding a second reporting tool the agent would have to choose between.
    path = "/reports/export-candidates" if view == "export_candidates" else "/reports/overview"

    payload, failure = await call_json(
        http_client,
        "GET",
        f"{base_url(context)}{path}",
        headers=context.headers,
        params=params,
        feature="read Expense Management reports",
    )
    if failure:
        return failure

    return list_result(
        payload,
        "rows",
        view=view,
        filters={
            "employee_id": employee_id,
            "department_id": department_id,
            "date_from": date_from,
            "date_to": date_to,
            "status": status,
        },
    )
