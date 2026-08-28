"""Search company documents through the documents application domain."""

from src.core.interfaces.http_client import HttpClient
from src.core.models.request_context import RequestContext
from src.core.models.types import Header
from src.shared.normalize import clean_text
from src.shared.result import error_result, ok_result


def _get_company_id(request_headers):
    if not isinstance(request_headers, dict):
        return None

    normalized_headers = {
        str(key).lower(): value
        for key, value in request_headers.items()
        if key is not None
    }
    return clean_text(normalized_headers.get(Header.X_COMPANY_ID))


async def run(task_args, context: RequestContext, http_client: HttpClient):
    api_base_url = context.api_base_url
    headers = context.headers

    task_args = task_args if isinstance(task_args, dict) else {}
    query = clean_text(task_args.get("query"))
    source = clean_text(task_args.get("source"))
    if not query:
        return error_result("Missing required field: query")

    company_id = _get_company_id(context.request_headers)
    if not company_id:
        return error_result("Missing required request header: xhr-company-id")

    search_url = f"{api_base_url}/v1/graphrag/documents/search"
    query_params = {
        "query": query,
        "company_id": company_id,
        "mode": "hybrid",
        "limit": 5,
    }
    if source:
        query_params["source"] = source

    async with http_client.session() as client:
        response = await client.get(search_url, params=query_params, headers=headers)
        try:
            payload = response.json()
        except Exception:
            payload = {}

    if response.status_code < 200 or response.status_code >= 300:
        return error_result(f"Company document search failed: {response.status_code} {str(payload)}")

    if isinstance(payload, dict):
        data = payload.get("data", payload)
        meta = payload.get("meta")
    else:
        data = payload
        meta = None

    return ok_result({
        "data": data,
        "meta": meta,
        "query": query_params,
    })
