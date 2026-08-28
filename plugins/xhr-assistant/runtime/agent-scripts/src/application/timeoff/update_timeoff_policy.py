from src.core.models.request_context import RequestContext
from src.core.interfaces.http_client import HttpClient
from src.shared.normalize import clean_float, clean_text
from src.shared.result import ok_result, error_result
from src.shared.http import format_error, request_json


async def run(task_args, context: RequestContext, http_client: HttpClient):
    api_base_url = context.api_base_url
    headers = context.headers

    task_args = task_args if isinstance(task_args, dict) else {}
    policy_id = clean_text(task_args.get("policy_id") or task_args.get("policyId") or task_args.get("id"))
    if not policy_id:
        return error_result("policy_id_required")

    name = clean_text(task_args.get("name") or task_args.get("policy_name"))
    allowance = clean_float(task_args.get("allowance") or task_args.get("annual_allowance"))
    accrual_frequency = clean_text(task_args.get("accrual_frequency") or task_args.get("accrualFrequency"))
    description = clean_text(task_args.get("description"))

    body = {}
    if name:
        body["name"] = name
    if allowance is not None:
        body["allowance"] = allowance
    if accrual_frequency:
        body["accrualFrequency"] = accrual_frequency
    if description is not None:
        body["description"] = description

    endpoint = f"{api_base_url}/v1/to/time-off-policies/{policy_id}"

    async with http_client.session() as client:
        try:
            status_code, payload = await request_json(client, "PUT", endpoint, json_data=body, headers=headers)
        except Exception as exc:
            return error_result(str(format_error(exc=exc)))

    if status_code >= 400:
        return error_result(str(format_error(payload)))

    return ok_result({
        "status": "UPDATED",
        "policy_id": policy_id,
        "response": payload.get("data") if isinstance(payload, dict) else payload,
    })
