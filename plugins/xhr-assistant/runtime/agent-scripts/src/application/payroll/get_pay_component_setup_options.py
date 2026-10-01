from __future__ import annotations

from typing import Any

from src.core.interfaces.http_client import HttpClient
from src.core.models.request_context import RequestContext
from src.shared.http import FetchJsonError, fetch_json
from src.shared.result import ok_result


DEFAULT_SYSTEM_FORMULA_VARIABLES: list[dict[str, Any]] = [
    {"label": "Base Salary", "value": "${base_salary}", "data_type": "NUMBER"},
    {"label": "Gross Salary", "value": "${gross_salary}", "data_type": "NUMBER"},
    {"label": "Net Salary", "value": "${net_salary}", "data_type": "NUMBER"},
    {"label": "Standard Work Days", "value": "${standard_work_days}", "data_type": "NUMBER"},
    {"label": "Actual Work Days", "value": "${actual_work_days}", "data_type": "NUMBER"},
]


def _to_trimmed_string(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, (str, int, float)):
        trimmed = str(value).strip()
        return trimmed if trimmed else None
    return None


def _format_payroll_work_location(loc: dict[str, Any]) -> dict[str, Any]:
    loc_id = _to_trimmed_string(loc.get("id")) or ""
    loc_name = _to_trimmed_string(loc.get("name"))
    currency = _to_trimmed_string(loc.get("currency"))
    country = loc.get("country") if isinstance(loc.get("country"), dict) else {}
    country_name = _to_trimmed_string(country.get("name"))
    country_iso_code = _to_trimmed_string(country.get("iso_code") or country.get("isoCode"))
    city = loc.get("city") if isinstance(loc.get("city"), dict) else {}
    city_name = _to_trimmed_string(city.get("name")) if isinstance(city, dict) else _to_trimmed_string(loc.get("city"))

    return {
        "id": loc_id,
        "name": loc_name,
        "currency": currency,
        "country_name": country_name,
        "country_iso_code": country_iso_code,
        "city_name": city_name,
    }


async def run(task_args: Any, context: RequestContext, http_client: HttpClient) -> dict[str, Any]:
    del task_args
    api_base_url = context.api_base_url
    headers = context.headers

    locations_url = f"{api_base_url}/v1/cm/locations/active"
    formula_vars_url = f"{api_base_url}/v1/pr/formula-variables"

    locations_raw: list[dict[str, Any]] = []
    formula_vars_data: dict[str, Any] = {"system_variables": DEFAULT_SYSTEM_FORMULA_VARIABLES, "pay_components": []}

    async with http_client.session() as client:
        # Fetch active locations
        try:
            payload = await fetch_json(client, locations_url, headers=headers)
            if isinstance(payload, dict):
                data = payload.get("data")
                if isinstance(data, list):
                    locations_raw = [item for item in data if isinstance(item, dict)]
        except FetchJsonError:
            try:
                fallback_url = f"{api_base_url}/v1/cm/locations"
                payload = await fetch_json(client, fallback_url, headers=headers)
                if isinstance(payload, dict):
                    data = payload.get("data")
                    if isinstance(data, list):
                        locations_raw = [item for item in data if isinstance(item, dict)]
            except FetchJsonError:
                pass
        except Exception:
            pass

        # Fetch formula variables
        try:
            payload = await fetch_json(client, formula_vars_url, headers=headers)
            if isinstance(payload, dict):
                data = payload.get("data")
                if isinstance(data, dict):
                    formula_vars_data = data
        except Exception:
            pass

    locations_formatted = [_format_payroll_work_location(item) for item in locations_raw]

    return ok_result({
        "payroll_formula_variables": formula_vars_data,
        "payroll_work_locations": locations_formatted,
        "current_pay_component": None,
    })
