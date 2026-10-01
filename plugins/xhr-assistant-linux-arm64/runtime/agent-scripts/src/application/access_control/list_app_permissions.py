from src.core.models.request_context import RequestContext
from src.core.interfaces.http_client import HttpClient
from src.shared.normalize import clean_text
from src.shared.result import ok_result, error_result

from ._client import (
    describe_error,
    get_permission_settings,
    list_installed_apps,
    parse_blocks,
    resolve_app,
    settings_version,
)


async def run(task_args, context: RequestContext, http_client: HttpClient):
    args = task_args if isinstance(task_args, dict) else {}
    wanted = clean_text(args.get("app"))

    status_code, apps = await list_installed_apps(context, http_client)
    if status_code < 200 or status_code >= 300:
        return error_result(f"Installed apps request failed: HTTP {status_code}")
    if not apps:
        return ok_result({"app_count": 0, "apps": [], "note": "No apps are installed for this company."})

    if wanted:
        app, failure = resolve_app(apps, wanted)
        if failure:
            return error_result(failure)
        targets = [app]
    else:
        targets = apps

    results = []
    for app in targets:
        status_code, payload = await get_permission_settings(context, http_client, app["app_id"])
        if status_code < 200 or status_code >= 300:
            results.append({**app, "error": describe_error(status_code, payload)})
            continue
        results.append(
            {
                **app,
                "settings_version": settings_version(payload),
                "data_blocks": parse_blocks(payload),
            }
        )

    return ok_result(
        {
            "app_count": len(results),
            "apps": results,
            "notes": [
                "relations listed under a block are the relations currently granted that operation",
                "company:admin is always granted and cannot be revoked",
                "an operation with supported=false cannot be granted on that block",
            ],
        }
    )
