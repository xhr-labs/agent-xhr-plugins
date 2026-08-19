from src.core.models.request_context import RequestContext
from src.core.interfaces.http_client import HttpClient
from src.shared.result import ok_result, error_result


def _format_page(page):
    if not isinstance(page, dict):
        return None

    children = page.get("children")
    if not isinstance(children, list):
        children = []

    formatted_children = []
    for child in children:
        formatted_child = _format_page(child)
        if formatted_child is not None:
            formatted_children.append(formatted_child)

    return {
        "page_id": page.get("id"),
        "parent_page_id": page.get("parent_id"),
        "title": page.get("title"),
        "children": formatted_children,
    }


async def run(task_args, context: RequestContext, http_client: HttpClient):
    api_base_url = context.api_base_url
    headers = context.headers

    url = f"{api_base_url}/v1/pm/company-wiki/pages/hierarchy"

    async with http_client.session() as client:
        response = await client.get(url, headers=headers)
        try:
            payload = response.json()
        except Exception:
            payload = {}

    if isinstance(payload, dict):
        data = payload.get("data") or []
    else:
        data = []

    if not isinstance(data, list):
        data = []

    formatted_data = []
    for item in data:
        formatted_item = _format_page(item)
        if formatted_item is not None:
            formatted_data.append(formatted_item)

    if response.status_code < 200 or response.status_code >= 300:
        return error_result(f"Company page hierarchy request failed: {response.status_code} {str(payload)}",)

    return ok_result({
        "data_count": len(formatted_data),
        "data": formatted_data,
    })
