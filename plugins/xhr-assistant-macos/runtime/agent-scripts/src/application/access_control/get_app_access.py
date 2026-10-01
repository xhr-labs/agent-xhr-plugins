from src.core.models.request_context import RequestContext
from src.core.interfaces.http_client import HttpClient
from src.shared.normalize import clean_text
from src.shared.result import ok_result, error_result

from ._client import describe_error, get_access_settings, list_installed_apps, resolve_app


def _describe(groups):
    if not groups:
        return "All employees (no group restriction stored)"
    if "ADMIN" in groups and len(groups) == 1:
        return "Admins only"
    return "Restricted to: " + ", ".join(groups)


async def run(task_args, context: RequestContext, http_client: HttpClient):
    args = task_args if isinstance(task_args, dict) else {}
    wanted = clean_text(args.get("app"))

    status_code, apps = await list_installed_apps(context, http_client)
    if status_code < 200 or status_code >= 300:
        return error_result(f"Installed apps request failed: HTTP {status_code}")
    if not apps:
        return ok_result({"app_count": 0, "apps": []})

    if wanted:
        app, failure = resolve_app(apps, wanted)
        if failure:
            return error_result(failure)
        targets = [app]
    else:
        targets = apps

    results = []
    for app in targets:
        status_code, payload = await get_access_settings(context, http_client, app["app_id"])
        if status_code < 200 or status_code >= 300:
            results.append({**app, "error": describe_error(status_code, payload)})
            continue
        data = payload.get("data") if isinstance(payload, dict) else None
        groups = ((data or {}).get("access") or {}).get("groups") or []
        results.append({**app, "groups": list(groups), "summary": _describe(list(groups))})

    return ok_result({"app_count": len(results), "apps": results})
