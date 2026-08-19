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

    allowance = clean_float(task_args.get("allowance") or task_args.get("annual_allowance")) or 12.0
    accrual_frequency = clean_text(task_args.get("accrual_frequency") or task_args.get("accrualFrequency")) or "MONTHLY"
    description = clean_text(task_args.get("description"))

    body = {
        "name": name,
        "timeOffTypeId": time_off_type_id,
        "allowance": allowance,
        "accrualFrequency": accrual_frequency,
    }
    if description:
        body["description"] = description

    endpoint = f"{api_base_url}/v1/to/time-off-policies"

    async with http_client.session() as client:
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
