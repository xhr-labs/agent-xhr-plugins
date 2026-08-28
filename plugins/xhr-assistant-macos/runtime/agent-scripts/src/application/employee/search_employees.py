from src.core.models.request_context import RequestContext
from src.core.interfaces.http_client import HttpClient
from src.shared.normalize import clean_text, to_bool
from src.shared.result import ok_result, error_result


async def run(task_args, context: RequestContext, http_client: HttpClient):
    api_base_url = context.api_base_url
    headers = context.headers

    task_args = task_args if isinstance(task_args, dict) else {}
    name = clean_text(task_args.get("name"))
    include_line_manager_value = task_args.get("includeLineManager")
    include_line_manager = (
        True
        if include_line_manager_value is None
        else to_bool(include_line_manager_value)
    )

    if not name:
        return error_result("Name parameter is required",)

    query_params = {
        "name": name,
        "pageSize": 20,
        "pageNumber": 0,
    }

    employees_url = f"{api_base_url}/v1/bff/employees"

    async with http_client.session() as client:
        response = await client.get(employees_url, params=query_params, headers=headers)
        try:
            payload = response.json()
        except Exception:
            payload = {}
        finally:
            await response.aclose()

        async def fetch_line_manager(employee_id):
            if not employee_id:
                return None
            detail_url = f"{api_base_url}/v1/bff/employees/{employee_id}"
            detail_params = {"includeCustomField": "true"}
            detail_resp = await client.get(detail_url, params=detail_params, headers=headers)
            try:
                detail_payload = detail_resp.json()
            except Exception:
                return None
            finally:
                await detail_resp.aclose()

            if isinstance(detail_payload, dict):
                detail_data = detail_payload.get("data")
                if isinstance(detail_data, dict):
                    return detail_data.get("line_manager")
            return None

        if isinstance(payload, dict):
            data = payload.get("data") or []
            meta = payload.get("meta")
        else:
            data = []
            meta = None

        if include_line_manager and isinstance(data, list):
            for item in data:
                if not isinstance(item, dict):
                    continue
                employee_id = item.get("id") or item.get("employee_id")
                line_manager = await fetch_line_manager(employee_id)
                if line_manager is not None:
                    item["line_manager"] = line_manager
        elif include_line_manager and isinstance(data, dict):
            employee_id = data.get("id") or data.get("employee_id")
            line_manager = await fetch_line_manager(employee_id)
            if line_manager is not None:
                data["line_manager"] = line_manager

        status_code = response.status_code

    if status_code < 200 or status_code >= 300:
        return error_result(f"Employee search failed: {status_code} {str(payload)}",)

    return ok_result({
        "data": data,
        "nextAction": "review_search_results",
        "meta": meta,
        "query": query_params,
    })


