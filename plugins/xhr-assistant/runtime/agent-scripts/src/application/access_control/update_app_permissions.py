from src.core.models.request_context import RequestContext
from src.core.interfaces.http_client import HttpClient
from src.shared.normalize import clean_text, normalize_list
from src.shared.result import ok_result, error_result

from ._client import (
    ADMIN_RELATION,
    OPERATIONS,
    describe_error,
    get_permission_settings,
    list_installed_apps,
    parse_blocks,
    put_permission_settings,
    resolve_app,
    settings_version,
    to_payload_blocks,
)

ACTIONS = ("grant", "revoke", "replace")


def _block_match_key(value):
    return "".join("-" if char in " _" else char for char in str(value or "").strip().lower())


def _resolve_block(blocks, wanted_block):
    wanted_key = _block_match_key(wanted_block)
    matches = []
    for block in blocks:
        candidates = {_block_match_key(block.get("block")), _block_match_key(block.get("label"))}
        if wanted_key in candidates:
            matches.append(block)
    return matches[0] if len(matches) == 1 else None


def _apply(current, relations, action):
    if action == "grant":
        merged = list(current)
        for relation in relations:
            if relation not in merged:
                merged.append(relation)
        return merged
    if action == "revoke":
        return [relation for relation in current if relation not in relations]
    return list(dict.fromkeys(relations))


async def run(task_args, context: RequestContext, http_client: HttpClient):
    args = task_args if isinstance(task_args, dict) else {}
    wanted_app = clean_text(args.get("app"))
    wanted_block = clean_text(args.get("block"))
    operation = (clean_text(args.get("operation")) or "").lower()
    action = (clean_text(args.get("action")) or "").lower()
    relations = normalize_list(args.get("relations"))

    if operation not in OPERATIONS:
        return error_result(f"operation must be one of: {', '.join(OPERATIONS)}")
    if action not in ACTIONS:
        return error_result(f"action must be one of: {', '.join(ACTIONS)}")
    if not relations:
        return error_result(
            "relations is required (comma-separated, for example 'company:hr,location:leader')"
        )
    if not wanted_block:
        return error_result("block is required")

    status_code, apps = await list_installed_apps(context, http_client)
    if status_code < 200 or status_code >= 300:
        return error_result(f"Installed apps request failed: HTTP {status_code}")

    app, failure = resolve_app(apps, wanted_app)
    if failure:
        return error_result(failure)

    status_code, payload = await get_permission_settings(context, http_client, app["app_id"])
    if status_code < 200 or status_code >= 300:
        return error_result(f"Current permissions request failed: {describe_error(status_code, payload)}")

    blocks = parse_blocks(payload)
    if not blocks:
        return error_result(f"{app['app_name']} has no configurable data blocks.")

    target = _resolve_block(blocks, wanted_block)
    if target is None:
        names = ", ".join(str(b["block"]) for b in blocks)
        return error_result(
            f"Data block '{wanted_block}' does not exist on {app['app_name']}. Blocks: {names}"
        )

    if not target[operation]["supported"]:
        return error_result(
            f"{app['app_name']} does not support '{operation}' on block '{target['block']}'. "
            "The API accepts such a payload but silently drops it."
        )

    selectable = target["selectable_relations"]
    unknown = [relation for relation in relations if relation not in selectable]
    if unknown:
        return error_result(
            f"Relation(s) {', '.join(unknown)} cannot be used on block '{target['block']}'. "
            f"Selectable relations: {', '.join(selectable)}"
        )

    before = list(target[operation]["relations"])
    desired = _apply(before, relations, action)

    blocked_admin = (
        action in ("revoke", "replace")
        and ADMIN_RELATION in before
        and ADMIN_RELATION not in desired
    )
    if ADMIN_RELATION not in desired:
        desired.append(ADMIN_RELATION)

    if sorted(desired) == sorted(before):
        note = (
            f"{ADMIN_RELATION} cannot be revoked; the platform always keeps it. Nothing was sent."
            if blocked_admin
            else "Requested state already matches the stored configuration; nothing was sent."
        )
        return ok_result(
            {
                **app,
                "block": target["block"],
                "operation": operation,
                "changed": False,
                "relations": before,
                "note": note,
            }
        )

    target[operation]["relations"] = desired

    # The API replaces the whole configuration: every block must be resent or it
    # is silently reset to company:admin only.
    status_code, response_payload = await put_permission_settings(
        context, http_client, app["app_id"], to_payload_blocks(blocks)
    )
    if status_code < 200 or status_code >= 300:
        return error_result(f"Permission update failed: {describe_error(status_code, response_payload)}")

    verify_status, verify_payload = await get_permission_settings(context, http_client, app["app_id"])
    if verify_status < 200 or verify_status >= 300:
        return error_result(
            f"Permission update was sent, but read-back verification failed: "
            f"{describe_error(verify_status, verify_payload)}"
        )

    saved = parse_blocks(verify_payload)
    saved_target = next((b for b in saved if b["block"] == target["block"]), None)
    after = saved_target[operation]["relations"] if saved_target else desired

    warnings = []
    if blocked_admin:
        warnings.append(f"{ADMIN_RELATION} cannot be revoked; the platform always keeps it.")

    return ok_result(
        {
            **app,
            "settings_version": settings_version(verify_payload),
            "block": target["block"],
            "block_label": target["label"],
            "operation": operation,
            "action": action,
            "changed": True,
            "relations_before": before,
            "relations_after": after,
            "all_blocks_after": saved,
            "warnings": warnings,
        }
    )
