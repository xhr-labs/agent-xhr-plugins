from datetime import datetime, timezone

from src.core.models.request_context import RequestContext
from src.core.interfaces.http_client import HttpClient
from src.core.models.types import Header
from src.shared.normalize import clean_int, clean_text
from src.shared.result import ok_result, error_result


def _format_location(location):
    if not isinstance(location, dict):
        return None

    country = location.get("country") or {}
    return {
        "locationId": location.get("id"),
        "name": location.get("name"),
        "type": location.get("location_type"),
        "isActive": location.get("is_active"),
        "countryName": country.get("name"),
        "countryIsoCode": country.get("iso_code"),
    }


def _format_holidays(entries):
    formatted = []
    if not isinstance(entries, list):
        return formatted

    for entry in entries:
        if not isinstance(entry, dict):
            continue
        formatted.append({
            "holidayId": entry.get("id"),
            "name": entry.get("name"),
            "date": entry.get("date"),
            "description": entry.get("description"),
        })
    return formatted


async def run(task_args, context: RequestContext, http_client: HttpClient):
    api_base_url = context.api_base_url
    headers = context.headers

    task_args = task_args if isinstance(task_args, dict) else {}
    employee_id = clean_text(context.request_headers.get(Header.X_EMPLOYEE_ID))
    requested_year = clean_int(task_args.get("year"))
    if requested_year is None:
        requested_year = datetime.now(timezone.utc).year

    if not employee_id:
        return error_result("missing_employee_id",)

    employee_url = f"{api_base_url}/v1/em/employees/{employee_id}"

    async with http_client.session() as client:
        employee_response = await client.get(employee_url, headers=headers)

        try:
            employee_payload = employee_response.json()
        except Exception:
            employee_payload = {}

        if isinstance(employee_payload, dict):
            employee_data = employee_payload.get("data") or {}
            meta = employee_payload.get("meta")
        else:
            employee_data = {}
            meta = None

        work_location = employee_data.get("work_location") if isinstance(employee_data, dict) else None

        if isinstance(work_location, dict):
            location_id = clean_text(work_location.get("id"))
        else:
            location_id = None

        formatted_location = _format_location(work_location)

        if not location_id:
            return ok_result({
                "data": {
                    "employeeId": employee_id,
                    "employeeName": employee_data.get("full_name"),
                    "workLocation": formatted_location,
                    "holidays": [],
                    "holidayCount": 0,
                    "year": requested_year,
                },
                "nextAction": "work_location_not_found",
                "meta": meta,
                "query": {"employeeEndpoint": employee_url},
            })

        holidays_url = f"{api_base_url}/v1/cm/locations/{location_id}/holidays"
        holidays_params = {"year": requested_year}
        holidays_response = await client.get(holidays_url, params=holidays_params, headers=headers)

    try:
        holidays_payload = holidays_response.json()
    except Exception:
        holidays_payload = {}

    if isinstance(holidays_payload, dict):
        holidays = holidays_payload.get("data") or []
        holidays_meta = holidays_payload.get("meta")
    else:
        holidays = []
        holidays_meta = None

    formatted_holidays = _format_holidays(holidays)
    holiday_count = len(formatted_holidays)

    if holidays_response.status_code < 200 or holidays_response.status_code >= 300:
        return error_result(f"Public holidays request failed: {holidays_response.status_code} {str(holidays_payload)}",)

    return ok_result({
        "data": {
            "employeeId": employee_id,
            "employeeName": employee_data.get("full_name"),
            "workLocation": formatted_location,
            "holidays": formatted_holidays,
            "holidayCount": holiday_count,
            "year": requested_year,
        },
        "nextAction": "share_public_holidays",
        "meta": holidays_meta,
        "query": {
            "employeeEndpoint": employee_url,
            "holidaysEndpoint": holidays_url,
            "holidaysParams": {"year": requested_year},
        },
    })

