from __future__ import annotations

import re
from typing import Any

from src.core.interfaces.http_client import HttpClient
from src.core.models.request_context import RequestContext
from src.shared.http import FetchJsonError, fetch_json
from src.shared.result import error_result, ok_result


def _to_trimmed_string(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, (str, int, float)):
        trimmed = str(value).strip()
        return trimmed if trimmed else None
    return None


def _unique_strings(values: list[Any]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in values:
        s = _to_trimmed_string(item)
        if s and s not in seen:
            seen.add(s)
            result.append(s)
    return result


def _build_employment_type_aliases(name: Any) -> list[str]:
    trimmed = _to_trimmed_string(name)
    if not trimmed:
        return []
    return _unique_strings([
        trimmed,
        trimmed.lower(),
        trimmed.replace("-", " "),
        re.sub(r"\s+", "-", trimmed),
    ])


def _build_time_off_type_aliases(name: Any) -> list[str]:
    trimmed = _to_trimmed_string(name)
    if not trimmed:
        return []
    return _unique_strings([
        trimmed,
        trimmed.lower(),
        re.sub(r"\s+", " ", trimmed),
    ])


def _format_location_option(loc: dict[str, Any]) -> dict[str, Any]:
    loc_id = _to_trimmed_string(loc.get("id")) or ""
    loc_name = _to_trimmed_string(loc.get("name"))
    country = loc.get("country") if isinstance(loc.get("country"), dict) else {}
    country_name = _to_trimmed_string(country.get("name"))
    country_iso_code = _to_trimmed_string(country.get("iso_code") or country.get("isoCode"))
    country_code = _to_trimmed_string(country.get("country_code") or country.get("countryCode"))
    city = _to_trimmed_string(loc.get("city"))
    district = _to_trimmed_string(loc.get("district"))
    street = _to_trimmed_string(loc.get("street"))
    additional_street = _to_trimmed_string(loc.get("additional_street") or loc.get("additionalStreet"))
    building_number = _to_trimmed_string(loc.get("building_number") or loc.get("buildingNumber"))
    zip_code = _to_trimmed_string(loc.get("zip_code") or loc.get("zipCode"))
    location_type = _to_trimmed_string(loc.get("location_type") or loc.get("locationType")) or ""

    label = loc_name or country_name or loc_id

    combo1 = f"{city} {country_name}" if city and country_name else None
    combo2 = f"{district} {country_name}" if district and country_name else None
    combo3 = f"{loc_name} {country_name}" if loc_name and country_name else None

    raw_aliases = [
        label,
        loc_name,
        city,
        district,
        street,
        additional_street,
        building_number,
        zip_code,
        country_name,
        country_iso_code,
        country_code,
        location_type,
        combo1,
        combo2,
        combo3,
    ]
    aliases = _unique_strings(raw_aliases)

    return {
        "id": loc_id,
        "label": label,
        "name": loc_name,
        "city": city,
        "district": district,
        "street": street,
        "additional_street": additional_street,
        "building_number": building_number,
        "zip_code": zip_code,
        "country_name": country_name,
        "country_iso_code": country_iso_code,
        "country_code": country_code,
        "location_type": location_type,
        "aliases": aliases,
        "match_text": " | ".join(aliases),
    }


def _format_employment_type_option(emp: dict[str, Any]) -> dict[str, Any]:
    emp_id = _to_trimmed_string(emp.get("id")) or ""
    emp_name = _to_trimmed_string(emp.get("name")) or emp_id
    aliases = _build_employment_type_aliases(emp_name)

    return {
        "id": emp_id,
        "name": emp_name,
        "aliases": aliases,
        "match_text": " | ".join(aliases),
    }


def _format_time_off_type_option(tot: dict[str, Any]) -> dict[str, Any]:
    tot_id = _to_trimmed_string(tot.get("id")) or ""
    tot_name = _to_trimmed_string(tot.get("name")) or tot_id
    aliases = _build_time_off_type_aliases(tot_name)

    return {
        "id": tot_id,
        "name": tot_name,
        "aliases": aliases,
        "match_text": " | ".join(aliases),
    }


async def run(task_args: Any, context: RequestContext, http_client: HttpClient) -> dict[str, Any]:
    del task_args
    api_base_url = context.api_base_url
    headers = context.headers

    locations_url = f"{api_base_url}/v1/cm/locations/active"
    emp_types_url = f"{api_base_url}/v1/cm/employee-types"
    time_off_types_url = f"{api_base_url}/v1/to/time-off-types"

    locations_raw: list[dict[str, Any]] = []
    emp_types_raw: list[dict[str, Any]] = []
    time_off_types_raw: list[dict[str, Any]] = []

    async with http_client.session() as client:
        # Fetch locations
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

        # Fetch employment types
        try:
            payload = await fetch_json(client, emp_types_url, headers=headers)
            if isinstance(payload, dict):
                data = payload.get("data")
                if isinstance(data, list):
                    emp_types_raw = [item for item in data if isinstance(item, dict)]
        except FetchJsonError:
            try:
                fallback_url = f"{api_base_url}/v1/cm/employment-types"
                payload = await fetch_json(client, fallback_url, headers=headers)
                if isinstance(payload, dict):
                    data = payload.get("data")
                    if isinstance(data, list):
                        emp_types_raw = [item for item in data if isinstance(item, dict)]
            except FetchJsonError:
                pass
        except Exception:
            pass

        # Fetch time off types
        try:
            payload = await fetch_json(
                client, time_off_types_url, method="GET", params={"page": 0, "size": 200}, headers=headers
            )
            if isinstance(payload, dict):
                data = payload.get("data")
                if isinstance(data, list):
                    time_off_types_raw = [item for item in data if isinstance(item, dict)]
        except Exception:
            pass

    locations_formatted = [_format_location_option(item) for item in locations_raw]
    emp_types_formatted = [_format_employment_type_option(item) for item in emp_types_raw]
    time_off_types_formatted = [_format_time_off_type_option(item) for item in time_off_types_raw]

    return ok_result({
        "timeoff_policy_options": {
            "locations": locations_formatted,
            "employment_types": emp_types_formatted,
            "time_off_types": time_off_types_formatted,
        }
    })
