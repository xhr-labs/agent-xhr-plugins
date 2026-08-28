from src.core.models.request_context import RequestContext
from src.core.interfaces.http_client import HttpClient
from src.shared.normalize import clean_text
from src.shared.result import ok_result, error_result
import src.application.vdr.get_audit_logs as get_audit_logs


def _flatten_entry(entry):
    if not isinstance(entry, dict):
        return None

    file_info = entry.get("file") or {}
    data_room_info = entry.get("data_room") or {}
    triggered_by = entry.get("triggered_by") or {}

    return {
        "target_type": entry.get("target_type"),
        "action": entry.get("action"),
        "file_id": file_info.get("id") if isinstance(file_info, dict) else None,
        "file_name": file_info.get("name") if isinstance(file_info, dict) else None,
        "folder": file_info.get("folder") if isinstance(file_info, dict) else None,
        "data_room": data_room_info.get("name") if isinstance(data_room_info, dict) else None,
        "user_id": triggered_by.get("id") if isinstance(triggered_by, dict) else None,
        "user_name": triggered_by.get("full_name") if isinstance(triggered_by, dict) else None,
    }


async def run(task_args, context: RequestContext, http_client: HttpClient):
    args = task_args if isinstance(task_args, dict) else {}
    data_room = clean_text(args.get("dataRoom"))
    start_date = get_audit_logs._to_created_at(args.get("startDate"), True)
    end_date = get_audit_logs._to_created_at(args.get("endDate"), False)

    page = 0
    size = 1000
    all_entries = []
    page_count = 0

    while True:
        payload = await get_audit_logs.run({
            "page": page,
            "size": size,
            "dataRoom": data_room,
            "startDate": start_date,
            "endDate": end_date,
        }, context, http_client)

        if not isinstance(payload, dict) or payload.get("ok") is not True:
            break

        data_block = payload.get("data") or {}
        data = data_block.get("data") or [] if isinstance(data_block, dict) else []
        if isinstance(data, list):
            all_entries.extend(data)

        meta = data_block.get("meta") or {} if isinstance(data_block, dict) else {}
        has_next = False
        if isinstance(meta, dict):
            has_next = bool(meta.get("has_next") or meta.get("hasNext"))

        page_count += 1
        if not has_next:
            break

        page += 1

    flattened_rows = []
    for entry in all_entries:
        flattened = _flatten_entry(entry)
        if flattened is not None:
            flattened_rows.append(flattened)

    groups = {}
    for row in flattened_rows:
        if row["target_type"] != "FILE" or row["action"] not in ("VIEWED", "DOWNLOADED"):
            continue
        key = (row["user_id"], row["user_name"], row["target_type"], row["action"], row["file_id"])
        group = groups.get(key)
        if group is None:
            groups[key] = {
                "user_id": row["user_id"],
                "user_name": row["user_name"],
                "target_type": row["target_type"],
                "action": row["action"],
                "file_id": row["file_id"],
                "file_name": row["file_name"],
                "folder": row["folder"],
                "data_room": row["data_room"],
                "activity_count": 1,
            }
        else:
            group["activity_count"] += 1
            # First non-null wins, matching the previous groupby "first" aggregation.
            for field in ("file_name", "folder", "data_room"):
                if group[field] is None and row[field] is not None:
                    group[field] = row[field]

    # Sort by group key with nulls last, matching the previous sorted groupby output.
    aggregated = [
        group
        for _, group in sorted(
            groups.items(),
            key=lambda item: tuple((value is None, str(value)) for value in item[0]),
        )
    ]

    return ok_result({
        "data_count": len(aggregated),
        "data": aggregated,
        "meta": {
            "pages_fetched": page_count,
            "page_size": size,
        },
        "filters": {
            "dataRoom": data_room,
            "target_type": "FILE",
            "action": ["VIEWED", "DOWNLOADED"],
            "startDate": start_date,
            "endDate": end_date,
        },
    })
