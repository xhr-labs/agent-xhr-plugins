from datetime import datetime, timezone
from src.core.models.request_context import RequestContext
from src.core.interfaces.http_client import HttpClient
from src.shared.normalize import clean_float, clean_text
from src.shared.result import ok_result, error_result
from src.shared.http import format_error, request_json


async def run(task_args, context: RequestContext, http_client: HttpClient):
    api_base_url = context.api_base_url
    headers = context.headers

    task_args = task_args if isinstance(task_args, dict) else {}
    name = clean_text(task_args.get("name") or task_args.get("policy_name"))
    if not name:
        return error_result("policy_name_required")

    time_off_type_id = clean_text(task_args.get("time_off_type_id") or task_args.get("timeOffTypeId"))
    if not time_off_type_id:
        return error_result("time_off_type_id_required")

    allowance = clean_float(task_args.get("allowance") or task_args.get("annual_allowance") or task_args.get("annualAllowance")) or 12.0
    accrual_period = clean_text(task_args.get("accrual_period") or task_args.get("accrualPeriod") or task_args.get("accrual_frequency") or task_args.get("accrualFrequency")) or "MONTHLY"
    if accrual_period not in ("MONTHLY", "YEARLY"):
        accrual_period = "MONTHLY"

    location_id = clean_text(task_args.get("applied_location_id") or task_args.get("appliedLocationId") or task_args.get("location_id"))
    effective_from = clean_text(task_args.get("effective_from") or task_args.get("effectiveFrom") or task_args.get("effective_date"))
    if not effective_from:
        effective_from = datetime.now(timezone.utc).strftime("%Y-%m-%dT00:00:00Z")
    elif len(effective_from) == 10:
        effective_from = f"{effective_from}T00:00:00Z"

    description = clean_text(task_args.get("description"))

    async with http_client.session() as client:
        if not location_id:
            try:
                status_code, payload = await request_json(client, "GET", f"{api_base_url}/v1/cm/locations/active", headers=headers)
                locs = payload.get("data") if isinstance(payload, dict) and isinstance(payload.get("data"), list) else []
                if locs and isinstance(locs[0], dict):
                    location_id = locs[0].get("id")
            except Exception:
                pass

        if not location_id:
            return error_result("applied_location_id_required")

        body = {
            "name": name,
            "time_off_type_id": time_off_type_id,
            "annual_allowance": allowance,
            "accrual_period": accrual_period,
            "accrual_year_starts_on": "CALENDAR_YEAR",
            "accrual_timing": "START",
            "applied_location_id": location_id,
            "employment_type_id": None,
            "proration_strategy": "BY_DAYS",
            "rounding_rule": "NONE",
            "block_probation_requests": True,
            "effective_from": effective_from,
            "eligibility_rule": {
                "conditions": [],
                "condition_mode": "ALL"
            }
        }
        if description:
            body["description"] = description

        endpoint = f"{api_base_url}/v1/to/time-off-policies"
        try:
            status_code, payload = await request_json(client, "POST", endpoint, json_data=body, headers=headers)
        except Exception as exc:
            return error_result(str(format_error(exc=exc)))

    if status_code >= 400:
        return error_result(str(format_error(payload)))

    return ok_result({
        "status": "CREATED",
        "policy": payload.get("data") if isinstance(payload, dict) else payload,
    })
