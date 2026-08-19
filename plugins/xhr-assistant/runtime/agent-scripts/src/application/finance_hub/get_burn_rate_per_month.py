from datetime import datetime, timezone

from src.core.models.request_context import RequestContext
from src.core.interfaces.http_client import HttpClient
from src.shared.auth import is_admin_group
from src.shared.normalize import clean_int
from src.shared.result import ok_result, error_result


def _format_columns(columns):
    formatted = []
    if not isinstance(columns, list):
        return formatted
    for column in columns:
        if not isinstance(column, dict):
            continue
        key = column.get("key")
        if not key:
            continue
        formatted.append({
            "key": key,
            "label": column.get("label"),
            "year": column.get("year"),
            "month": column.get("month"),
        })
    return formatted


def _format_expense_rows(rows, columns):
    formatted = []
    column_meta = _format_columns(columns)

    if not isinstance(rows, list):
        return formatted

    for row in rows:
        if not isinstance(row, dict):
            continue
        values = row.get("values")
        if not isinstance(values, dict):
            values = {}
        monthly_expenses = []
        for column in column_meta:
            key = column["key"]
            amount = values.get(key)
            if not isinstance(amount, (int, float)):
                amount = 0
            monthly_expenses.append({
                "key": key,
                "label": column.get("label"),
                "year": column.get("year"),
                "month": column.get("month"),
                "amount": amount,
            })

        formatted.append({
            "categoryId": row.get("category_id"),
            "categoryName": row.get("name"),
            "total": row.get("total"),
            "monthlyExpenses": monthly_expenses,
        })
    return formatted

async def run(task_args, context: RequestContext, http_client: HttpClient):
    api_base_url = context.api_base_url
    headers = context.headers

    if not is_admin_group(context.request_headers.get("xhr-employee-group")):
        return error_result("You do not have permission to access Finance Hub reports.",)

    task_args = task_args if isinstance(task_args, dict) else {}
    requested_year = clean_int(task_args.get("year"))
    if requested_year is None:
        requested_year = datetime.now(timezone.utc).year

    report_url = f"{api_base_url}/v1/fh/reports/expenses/category-matrix"
    query_params = {
        "year": requested_year,
        "type": "expense",
        "monthFrom": 1,
        "monthTo": 12,
    }

    async with http_client.session() as client:
        response = await client.get(report_url, params=query_params, headers=headers)

    try:
        payload = response.json()
    except Exception:
        payload = {}

    if isinstance(payload, dict):
        data = payload.get("data") or {}
        meta = payload.get("meta")
    else:
        data = {}
        meta = None

    rows = data.get("rows") if isinstance(data, dict) else []
    columns = data.get("columns") if isinstance(data, dict) else []
    totals = data.get("totals") if isinstance(data, dict) else {}
    currency = data.get("currency") if isinstance(data, dict) else None

    formatted_rows = _format_expense_rows(rows, columns)

    if response.status_code < 200 or response.status_code >= 300:
        return error_result(f"Burn rate request failed: {response.status_code} {str(payload)}",)

    return ok_result({
        "data": {
            "expensePerCategory": formatted_rows,
            "totals": totals if isinstance(totals, dict) else {},
            "currency": currency,
        },
        "nextAction": "review_burn_rate_per_month",
        "meta": meta,
        "query": {
            "endpoint": report_url,
            "parameters": query_params,
        },
    })


