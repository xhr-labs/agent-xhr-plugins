from src.core.models.request_context import RequestContext
from src.core.interfaces.http_client import HttpClient
from src.shared.result import ok_result, error_result


async def run(task_args, context: RequestContext, http_client: HttpClient):
    api_base_url = context.api_base_url
    headers = context.headers

    profile_url = f"{api_base_url}/v1/im/me"

    async with http_client.session() as client:
        response = await client.get(profile_url, headers=headers)
        try:
            payload = response.json()
        except Exception:
            payload = {}

    if isinstance(payload, dict):
        data = payload.get("data")
        meta = payload.get("meta")
    else:
        data = None
        meta = None

    if response.status_code < 200 or response.status_code >= 300:
        return error_result(f"Profile request failed: {response.status_code} {str(payload)}",)

    return ok_result({
        "data": data,
        "meta": meta,
        "query": {"endpoint": profile_url},
    })
