from src.core.models.request_context import RequestContext
from src.core.interfaces.http_client import HttpClient
from src.core.models.types import Header
from src.shared.result import ok_result, error_result


def _employee_record(data, employee_id):
    if not isinstance(data, list) or not employee_id:
        return None
    for item in data:
        if not isinstance(item, dict):
            continue
        if item.get("id") == employee_id or item.get("employee_id") == employee_id:
            return item
    return None


async def run(task_args, context: RequestContext, http_client: HttpClient):
    api_base_url = context.api_base_url
    headers = context.headers
    employee_id = context.request_headers.get(Header.X_EMPLOYEE_ID)

    profile_url = f"{api_base_url}/v1/im/me"
    employees_url = f"{api_base_url}/v1/bff/employees"

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

    profile_data = data if isinstance(data, dict) else {}
    profile_name = profile_data.get("name") or profile_data.get("full_name")
    enriched_employee = None
    if profile_name and employee_id:
        try:
            async with http_client.session() as client:
                employees_response = await client.get(
                    employees_url,
                    params={"name": profile_name, "pageSize": 20, "pageNumber": 0},
                    headers=headers,
                )
                try:
                    employees_payload = employees_response.json()
                except Exception:
                    employees_payload = {}
                if 200 <= employees_response.status_code < 300 and isinstance(employees_payload, dict):
                    enriched_employee = _employee_record(employees_payload.get("data"), employee_id)
        except Exception:
            enriched_employee = None

    if isinstance(enriched_employee, dict):
        data = {
            **profile_data,
            "employee_profile": enriched_employee,
            "hiring_date": enriched_employee.get("hiring_date"),
            "date_of_joining": enriched_employee.get("date_of_joining"),
        }

    return ok_result({
        "data": data,
        "meta": meta,
        "query": {
            "endpoint": profile_url,
            "employee_profile_endpoint": employees_url if enriched_employee else None,
        },
    })
