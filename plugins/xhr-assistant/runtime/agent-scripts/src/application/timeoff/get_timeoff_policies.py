from src.core.models.request_context import RequestContext
from src.core.interfaces.http_client import HttpClient
from src.shared.normalize import clean_text
from src.shared.result import ok_result, error_result
from src.shared.http import format_error, request_json


async def run(task_args, context: RequestContext, http_client: HttpClient):
    api_base_url = context.api_base_url
    headers = context.headers

    task_args = task_args if isinstance(task_args, dict) else {}
    time_off_type_id = clean_text(task_args.get("time_off_type_id") or task_args.get("timeOffTypeId"))

    endpoint = f"{api_base_url}/v1/to/time-off-policies"
    query_params = {}
    if time_off_type_id:
        query_params["timeOffTypeId.equals"] = time_off_type_id

    async with http_client.session() as client:
        try:
            status_code, payload = await request_json(client, "GET", endpoint, params=query_params, headers=headers)
        except Exception as exc:
            return error_result(str(format_error(exc=exc)))

    if status_code >= 400:
        return error_result(str(format_error(payload)))

    policies = payload.get("data") if isinstance(payload, dict) else payload
    if not isinstance(policies, list):
        policies = []

    formatted = []
    for p in policies:
        if not isinstance(p, dict):
            continue
        ttype = p.get("time_off_type") if isinstance(p.get("time_off_type"), dict) else {}
        formatted.append({
            "policy_id": p.get("id"),
            "name": p.get("name"),
            "time_off_type_id": ttype.get("id") or p.get("time_off_type_id"),
            "time_off_type_name": ttype.get("name") or p.get("time_off_type_name"),
            "allowance": p.get("allowance") or p.get("annual_allowance"),
            "accrual_frequency": p.get("accrual_frequency") or p.get("accrualFrequency"),
            "is_active": p.get("is_active", True),
            "effective_date": p.get("effective_date"),
        })

    return ok_result({
        "policies_count": len(formatted),
        "policies": formatted,
        "query": query_params,
    })
