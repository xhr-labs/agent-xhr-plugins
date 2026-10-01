from src.application.employee_requests.common import call_json, page_result, value
from src.core.models.request_context import RequestContext
from src.shared.normalize import clean_text
from src.shared.result import ok_result


async def run(task_args, context: RequestContext, http_client):
    args = task_args if isinstance(task_args, dict) else {}
    params = {"pageSize": max(1, min(int(value(args, "page_size", "pageSize") or 25), 100))}
    cursor = clean_text(value(args, "cursor"))
    if cursor:
        params["cursor"] = cursor
    payload, failure = await call_json(
        http_client, "GET", f"{context.api_base_url}/v1/erequest/backoffice/request-types",
        headers=context.headers, params=params,
    )
    if failure:
        return failure
    return ok_result(page_result(payload, "request_types"))
