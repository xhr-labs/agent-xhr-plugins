from src.core.models.request_context import RequestContext
from src.core.interfaces.http_client import HttpClient
from src.shared.result import ok_result, error_result


async def run(task_args, context: RequestContext, http_client: HttpClient):
    api_base_url = context.api_base_url
    headers = context.headers

    apps_url = f"{api_base_url}/v1/as/apps/installed/menu"
    events_url = f"{api_base_url}/v1/wes/workflow-events"

    async with http_client.session() as client:
        apps_resp = await client.get(apps_url, headers=headers)
        try:
            apps_payload = apps_resp.json()
        except Exception:
            apps_payload = {}
        finally:
            await apps_resp.aclose()

        if isinstance(apps_payload, dict):
            apps_data = apps_payload.get("data") or []
        else:
            apps_data = []

        app_ids = []
        for item in apps_data:
            if isinstance(item, dict):
                app_id = item.get("id")
                if app_id:
                    app_ids.append(app_id)

        request_body = {
            "app_ids": ["00000000-0000-0000-0000-000000000000"] + app_ids
        }

        events_resp = await client.post(events_url, json=request_body, headers=headers)
        try:
            events_payload = events_resp.json()
        except Exception:
            events_payload = {}
        finally:
            await events_resp.aclose()

    if isinstance(events_payload, dict):
        events_data = events_payload.get("data") or []
        meta = events_payload.get("meta")
    else:
        events_data = []
        meta = None

    output_events = []
    for item in events_data:
        if not isinstance(item, dict):
            continue
        output_events.append({
            "event_id": item.get("id"),
            "app_id": item.get("app_id"),
            "event_key": item.get("event_key"),
            "event_name": item.get("event_name"),
            "status": item.get("status"),
        })

    if events_resp.status_code < 200 or events_resp.status_code >= 300:
        return error_result(f"Workflow events request failed: {events_resp.status_code} {str(events_payload)}",)

    return ok_result({
        "data": output_events,
        "meta": meta,
        "query": {
            "apps_endpoint": apps_url,
            "events_endpoint": events_url,
            "app_ids": request_body["app_ids"],
        },
    })
