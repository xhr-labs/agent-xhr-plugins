"""Drill into one employee's expenses from the Expense Management report."""

from __future__ import annotations

from src.application.exm.common import (
    EXPENSE_STATUSES,
    as_args,
    base_url,
    call_json,
    date_range,
    list_result,
    paging,
    require_enum,
    require_uuid,
    value,
)
from src.core.interfaces.http_client import HttpClient
from src.core.models.request_context import RequestContext


async def run(task_args, context: RequestContext, http_client: HttpClient):
    args = as_args(task_args)

    employee_id, error = require_uuid(
        value(args, "employee_id", "employeeId"),
        "employee_id",
        lookup_hint="skills/exm/get_expense_report_overview or skills/employee/search_employees",
    )
    if error:
        return error

    date_from, date_to, error = date_range(args)
    if error:
        return error

    status, error = require_enum(value(args, "status"), "status", EXPENSE_STATUSES)
    if error:
        return error

    params = paging(args)
    if date_from:
        params["dateFrom"] = date_from
    if date_to:
        params["dateTo"] = date_to
    if status:
        params["status"] = status

    payload, failure = await call_json(
        http_client,
        "GET",
        f"{base_url(context)}/reports/employees/{employee_id}/expenses",
        headers=context.headers,
        params=params,
        feature="read another employee's expense report",
    )
    if failure:
        return failure

    return list_result(
        payload,
        "expenses",
        employee_id=employee_id,
        filters={"date_from": date_from, "date_to": date_to, "status": status},
    )
