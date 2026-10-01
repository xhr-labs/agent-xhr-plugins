from src.core.interfaces.http_client import HttpClient
from src.core.models.request_context import RequestContext
from src.shared.result import error_result, ok_result


async def run(task_args, context: RequestContext, http_client: HttpClient):
    api_base_url = context.api_base_url
    headers = context.headers

    query_params = {
        "depth": 5,
        "includeDeactivated": "false",
        "maxNodes": 1000,
    }
    org_chart_url = f"{api_base_url}/v1/em/employees/org-chart"

    async with http_client.session() as client:
        response = await client.get(org_chart_url, params=query_params, headers=headers)
        try:
            payload = response.json()
        except Exception:
            payload = {}
        finally:
            await response.aclose()

    if isinstance(payload, dict):
        data = payload.get("data")
    else:
        data = None

    if response.status_code < 200 or response.status_code >= 300:
        return error_result(
            f"Org chart request failed: {response.status_code} {str(payload)}",
        )

    return ok_result(
        {
            "data": data,
            "query": {
                "endpoint": org_chart_url,
                **query_params,
            },
        }
    )
