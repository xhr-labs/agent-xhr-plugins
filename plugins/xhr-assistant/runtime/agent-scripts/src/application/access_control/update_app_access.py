from src.core.models.request_context import RequestContext
from src.core.interfaces.http_client import HttpClient
from src.shared.normalize import clean_text, normalize_list
from src.shared.result import ok_result, error_result

from ._client import (
    ACCESS_GROUPS,
    UNRESTRICTED_ACCESS_GROUP_ALIASES,
    describe_error,
    get_access_settings,
    list_installed_apps,
    put_access_settings,
    resolve_app,
)


def _current_groups(payload):
    data = payload.get("data") if isinstance(payload, dict) else None
    return list(((data or {}).get("access") or {}).get("groups") or [])


async def run(task_args, context: RequestContext, http_client: HttpClient):
    args = task_args if isinstance(task_args, dict) else {}
    wanted_app = clean_text(args.get("app"))
    groups = [group.strip().upper() for group in normalize_list(args.get("groups"))]

    if not groups:
        return error_result(
            f"groups is required; use one of: {', '.join(ACCESS_GROUPS)}, "
            f"or {', '.join(UNRESTRICTED_ACCESS_GROUP_ALIASES)}"
        )

    if len(groups) == 1 and groups[0] in UNRESTRICTED_ACCESS_GROUP_ALIASES:
        desired = []
    else:
        invalid_alias_mix = [group for group in groups if group in UNRESTRICTED_ACCESS_GROUP_ALIASES]
        if invalid_alias_mix:
            return error_result(
                f"{', '.join(UNRESTRICTED_ACCESS_GROUP_ALIASES)} cannot be combined with named groups."
            )
        desired = list(dict.fromkeys(groups))

    invalid = [group for group in desired if group not in ACCESS_GROUPS]
    if invalid:
        return error_result(
            f"Unknown access group(s): {', '.join(invalid)}. Allowed groups: {', '.join(ACCESS_GROUPS)}. "
            f"Use {UNRESTRICTED_ACCESS_GROUP_ALIASES[0]} to clear the restriction. "
            "The API stores unknown values without an error, so they are rejected here."
        )

    status_code, apps = await list_installed_apps(context, http_client)
    if status_code < 200 or status_code >= 300:
        return error_result(f"Installed apps request failed: HTTP {status_code}")

    app, failure = resolve_app(apps, wanted_app)
    if failure:
        return error_result(failure)

    status_code, payload = await get_access_settings(context, http_client, app["app_id"])
    if status_code < 200 or status_code >= 300:
        return error_result(f"Current app access request failed: {describe_error(status_code, payload)}")

    before = _current_groups(payload)

    if sorted(desired) == sorted(before):
        return ok_result(
            {
                **app,
                "changed": False,
                "groups": before,
                "note": "Requested app access already matches the stored configuration; nothing was sent.",
            }
        )

    status_code, response_payload = await put_access_settings(
        context, http_client, app["app_id"], desired
    )
    if status_code < 200 or status_code >= 300:
        return error_result(f"App access update failed: {describe_error(status_code, response_payload)}")

    status_code, verify_payload = await get_access_settings(context, http_client, app["app_id"])
    after = _current_groups(verify_payload) if 200 <= status_code < 300 else desired

    return ok_result(
        {
            **app,
            "changed": True,
            "groups_before": before,
            "groups_after": after,
            "note": "App access controls who can open the app; it does not change data-block permissions.",
        }
    )
