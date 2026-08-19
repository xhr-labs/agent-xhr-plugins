from src.core.models.request_context import RequestContext
from src.core.interfaces.http_client import HttpClient
from src.shared.normalize import clean_text
from src.shared.result import ok_result, error_result
from src.shared.http import format_error, request_json


async def run(task_args, context: RequestContext, http_client: HttpClient):
    api_base_url = context.api_base_url
    headers = context.headers

    task_args = task_args if isinstance(task_args, dict) else {}
    policy_id = clean_text(task_args.get("policy_id") or task_args.get("policyId") or task_args.get("id"))
    if not policy_id:
        return error_result("policy_id_required")

    endpoint = f"{api_base_url}/v1/to/time-off-policies/{policy_id}/archive"

    async with http_client.session() as client:
        try:
            status_code, payload = await request_json(client, "POST", endpoint, headers=headers)
        except Exception as exc:
            return error_result(str(format_error(exc=exc)))

    if status_code >= 400:
        return error_result(str(format_error(payload)))

    return ok_result({
        "status": "ARCHIVED",
        "policy_id": policy_id,
        "message": f"Policy {policy_id} has been archived successfully.",
    })
