import asyncio
from datetime import datetime, timezone
from typing import Any, List, Optional, Set

from src.core.models.request_context import RequestContext
from src.core.interfaces.http_client import HttpClient
from src.shared.auth import is_admin_group
from src.shared.result import ok_result, error_result

NET_INCOME_TOKENS = {
    "netincome",
    "netincomeamount",
    "netincomevalue",
    "netincomeyear",
    "netprofit",
    "netprofitloss",
    "net_income",
}

EXPENDITURE_TOKENS = {
    "expense",
    "expenses",
    "expenditure",
    "expenditures",
    "spend",
    "spending",
    "costs",
    "burn",
}

COLLECTION_TOKENS = {
    "values",
    "data",
    "series",
    "points",
    "items",
    "entries",
    "records",
    "months",
}

NET_INCOME_VALUE_TOKENS = {
    "value",
    "amount",
    "y",
    "netincome",
    "net_income",
}

EXPENDITURE_VALUE_TOKENS = {
    "value",
    "amount",
    "y",
    "expense",
    "expenses",
    "expenditure",
    "expenditures",
    "spend",
}

HINT_KEYS = ("key", "name", "label", "metric", "seriesName", "title", "description")


def _normalize_key(value: Any) -> str:
    if not isinstance(value, str):
        return ""
    return "".join(ch for ch in value.lower() if ch.isalnum() or ch == "_")


def _matches_tokens(value: Any, tokens: Set[str]) -> bool:
    normalized = _normalize_key(value)
    return normalized in tokens


def _to_float(value: Any) -> Optional[float]:
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        trimmed = value.strip().replace(",", "")
        try:
            return float(trimmed)
        except ValueError:
            return None
    return None


def _collect_value(value: Any, results: List[float]) -> bool:
    number = _to_float(value)
    if number is None:
        return False
    results.append(number)
    return True


def _dict_has_label_hint(data: Any, label_tokens: Set[str]) -> bool:
    if not isinstance(data, dict):
        return False
    for hint_key in HINT_KEYS:
        if _matches_tokens(data.get(hint_key), label_tokens):
            return True
    return False


def _extract_from_known_points(chart_data: Any, field_name: str) -> Optional[List[float]]:
    if not isinstance(chart_data, dict):
        return None
    for key in ("data_points", "datapoints", "points"):
        candidate = chart_data.get(key)
        if isinstance(candidate, list):
            results = []
            for item in candidate:
                if not isinstance(item, dict):
                    continue
                _collect_value(item.get(field_name), results)
            if results:
                return results
    return None


def _extract_series_by_heuristic(chart_data: Any, label_tokens: Set[str], value_tokens: Set[str]) -> Optional[List[float]]:
    results: List[float] = []
    found = False

    def _walk(node: Any, in_context: bool = False) -> None:
        nonlocal found
        if isinstance(node, dict):
            local_context = in_context or _dict_has_label_hint(node, label_tokens)
            for key, value in node.items():
                normalized_key = _normalize_key(key)
                if _matches_tokens(key, label_tokens):
                    found = True
                    _walk(value, True)
                    continue
                if normalized_key in COLLECTION_TOKENS:
                    _walk(value, local_context)
                    continue
                if local_context and normalized_key in value_tokens:
                    if _collect_value(value, results):
                        found = True
                    continue
                _walk(value, local_context)
        elif isinstance(node, list):
            for item in node:
                _walk(item, in_context)
        else:
            if in_context and _collect_value(node, results):
                found = True

    _walk(chart_data)
    return results if found else None


def _extract_monthly_values(chart_data: Any, field_name: str, label_tokens: Set[str], value_tokens: Set[str]) -> Optional[List[float]]:
    if chart_data is None:
        return None
    known = _extract_from_known_points(chart_data, field_name)
    if known:
        return known
    return _extract_series_by_heuristic(chart_data, label_tokens, value_tokens)


def _extract_monthly_net_income(chart_data: Any) -> Optional[List[float]]:
    return _extract_monthly_values(chart_data, "net_income", NET_INCOME_TOKENS, NET_INCOME_VALUE_TOKENS)


def _extract_monthly_expenditures(chart_data: Any) -> Optional[List[float]]:
    return _extract_monthly_values(chart_data, "expenditures", EXPENDITURE_TOKENS, EXPENDITURE_VALUE_TOKENS)


async def run(task_args, context: RequestContext, http_client: HttpClient):
    api_base_url = context.api_base_url
    headers = context.headers

    if not is_admin_group(context.request_headers.get("xhr-employee-group")):
        return error_result("You do not have permission to access Finance Hub reports.",)

    current_year = datetime.now(timezone.utc).year
    metrics_url = f"{api_base_url}/v1/fh/reports/metrics"
    chart_url = f"{api_base_url}/v1/fh/reports/chart"

    metrics_params = {
        "periodType": "YEARLY",
        "year": current_year,
    }
    chart_params = {
        "periodType": "MONTHLY",
        "year": current_year,
    }

    async with http_client.session() as client:
        metrics_response, chart_response = await asyncio.gather(
            client.get(metrics_url, params=metrics_params, headers=headers),
            client.get(chart_url, params=chart_params, headers=headers),
        )

    try:
        metrics_payload = metrics_response.json()
    except Exception:
        metrics_payload = {}

    try:
        chart_payload = chart_response.json()
    except Exception:
        chart_payload = {}

    metrics_data = metrics_payload.get("data") if isinstance(metrics_payload, dict) else {}
    chart_data = chart_payload.get("data") if isinstance(chart_payload, dict) else None

    net_income_year = _to_float(metrics_data.get("net_income") if isinstance(metrics_data, dict) else None)
    currency = metrics_data.get("currency") if isinstance(metrics_data, dict) else None

    monthly_net_incomes = _extract_monthly_net_income(chart_data)
    if monthly_net_incomes is not None:
        monthly_net_income_total = sum(monthly_net_incomes)
        average_monthly_net_income = monthly_net_income_total / 12
    else:
        monthly_net_income_total = None
        average_monthly_net_income = None

    monthly_expenditures = _extract_monthly_expenditures(chart_data)
    if monthly_expenditures is not None:
        monthly_expenditure_total = sum(monthly_expenditures)
        average_monthly_expenditures = monthly_expenditure_total / 12
    else:
        monthly_expenditure_total = None
        average_monthly_expenditures = None

    if net_income_year is not None and average_monthly_expenditures not in (None, 0):
        runway_months = net_income_year / average_monthly_expenditures
    else:
        runway_months = None

    overall_status = max(metrics_response.status_code, chart_response.status_code)
    if overall_status < 200 or overall_status >= 300:
        return error_result(f"No runway request failed: {overall_status} metrics={str(metrics_payload)} chart={str(chart_payload)}",)

    return ok_result({
        "data": {
            "year": current_year,
            "currency": currency,
            "netIncomeYear": net_income_year,
            "monthlyNetIncomeTotal": monthly_net_income_total,
            "averageMonthlyNetIncome": average_monthly_net_income,
            "monthlyExpendituresTotal": monthly_expenditure_total,
            "averageMonthlyExpenditures": average_monthly_expenditures,
            "runwayMonths": runway_months,
        },
        "nextAction": "review_no_runway",
        "meta": {
            "metrics": metrics_payload.get("meta") if isinstance(metrics_payload, dict) else None,
            "chart": chart_payload.get("meta") if isinstance(chart_payload, dict) else None,
        },
        "query": {
            "metrics": {
                "endpoint": metrics_url,
                "parameters": metrics_params,
            },
            "chart": {
                "endpoint": chart_url,
                "parameters": chart_params,
            },
        },
    })


