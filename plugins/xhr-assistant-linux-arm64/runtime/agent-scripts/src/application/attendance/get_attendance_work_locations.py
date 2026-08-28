from __future__ import annotations

from typing import Any

from src.core.interfaces.http_client import HttpClient
from src.core.models.request_context import RequestContext
from src.shared.http import FetchJsonError, fetch_json
from src.shared.result import ok_result


def _to_trimmed_string(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, (str, int, float)):
        trimmed = str(value).strip()
        return trimmed if trimmed else None
    return None


def _format_location_option(loc: dict[str, Any]) -> dict[str, Any]:
    loc_id = _to_trimmed_string(loc.get("id")) or ""
    loc_name = _to_trimmed_string(loc.get("name"))
    country = loc.get("country") if isinstance(loc.get("country"), dict) else {}
    country_name = _to_trimmed_string(country.get("name"))
    country_iso_code = _to_trimmed_string(country.get("iso_code") or country.get("isoCode"))
    city = _to_trimmed_string(loc.get("city"))
    location_type = _to_trimmed_string(loc.get("location_type") or loc.get("locationType"))

    return {
        "id": loc_id,
        "name": loc_name,
        "city": city,
        "country_name": country_name,
        "country_iso_code": country_iso_code,
        "location_type": location_type,
    }


async def run(task_args: Any, context: RequestContext, http_client: HttpClient) -> dict[str, Any]:
    del task_args
    api_base_url = context.api_base_url
    headers = context.headers

    locations_url = f"{api_base_url}/v1/cm/locations/active"
    locations_raw: list[dict[str, Any]] = []

    async with http_client.session() as client:
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

    locations_formatted = [_format_location_option(item) for item in locations_raw]

    return ok_result({
        "attendance_work_locations": locations_formatted,
    })
