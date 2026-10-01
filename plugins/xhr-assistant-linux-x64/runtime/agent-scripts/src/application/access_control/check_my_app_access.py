from src.core.models.request_context import RequestContext
from src.core.interfaces.http_client import HttpClient
from src.shared.normalize import clean_text
from src.shared.result import ok_result, error_result

from ._client import list_installed_apps, resolve_app

_AUTHZ_PATH = "/v1/bff/grpc/authz.v1.AuthZService/GetAppAccessData"


async def run(task_args, context: RequestContext, http_client: HttpClient):
    args = task_args if isinstance(task_args, dict) else {}
    wanted = clean_text(args.get("app"))

    status_code, apps = await list_installed_apps(context, http_client)
    if status_code < 200 or status_code >= 300:
        return error_result(f"Installed apps request failed: HTTP {status_code}")

    app, failure = resolve_app(apps, wanted)
    if failure:
        return error_result(failure)

    url = f"{context.api_base_url}{_AUTHZ_PATH}"
    async with http_client.session() as client:
        response = await client.post(url, headers=context.headers, json={"appId": app["app_id"]})
        try:
            payload = response.json()
        except Exception:
            payload = {}

    if response.status_code < 200 or response.status_code >= 300:
        return error_result(f"Effective access request failed: HTTP {response.status_code} {payload}")

    data = payload.get("data") if isinstance(payload, dict) else None
    source = data if isinstance(data, dict) else payload

    blocks = []
    for block in source.get("dataBlocks") or []:
        if not isinstance(block, dict):
            continue
        viewable = block.get("viewable") or []
        editable = block.get("editable") or []
        blocks.append(
            {
                "block": block.get("name"),
                "scope": block.get("category"),
                "can_read": bool(viewable),
                "can_write": bool(editable),
                "readable_entity_count": len(viewable),
                "editable_entity_count": len(editable),
            }
        )

    return ok_result(
        {
            **app,
            "settings_version": source.get("version"),
            "data_blocks": blocks,
            "note": "This is the effective access of the signed-in user only; it cannot be queried for another employee.",
        }
    )
