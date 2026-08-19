"""List company documents through the GraphRAG REST API."""

from src.core.interfaces.http_client import HttpClient
from src.core.models.request_context import RequestContext
from src.core.models.types import Header
from src.shared.normalize import clean_text
from src.shared.result import error_result, ok_result


def _request_header(request_headers, name):
    if not isinstance(request_headers, dict):
        return None
    normalized_headers = {
        str(key).lower(): value
        for key, value in request_headers.items()
        if key is not None
    }
    header_name = name.value if hasattr(name, "value") else str(name)
    return clean_text(normalized_headers.get(header_name.lower()))


async def run(task_args, context: RequestContext, http_client: HttpClient):
    del task_args

    company_id = _request_header(context.request_headers, Header.X_COMPANY_ID)
    if not company_id:
        return error_result("Missing required request header: xhr-company-id")

    employee_id = _request_header(context.request_headers, Header.X_EMPLOYEE_ID)
    headers = dict(context.headers)
    headers["Xhr-Company-Id"] = company_id
    if employee_id:
        headers["Xhr-Employee-Id"] = employee_id

    list_url = f"{context.api_base_url}/v1/graphrag/documents"
    query_params = {
        "company_id": company_id,
        "source": "company_document",
    }

    async with http_client.session() as client:
        response = await client.get(list_url, params=query_params, headers=headers)
        try:
            payload = response.json()
        except Exception:
            payload = {}

    if response.status_code < 200 or response.status_code >= 300:
        return error_result(f"List company documents failed: {response.status_code} {str(payload)}")

    documents = payload.get("documents") if isinstance(payload, dict) else None
    if not isinstance(documents, list):
        return error_result("Invalid list company documents response: documents must be a list")

    return ok_result({
        "documents": documents,
        "documents_count": len(documents),
        "query": query_params,
    })
