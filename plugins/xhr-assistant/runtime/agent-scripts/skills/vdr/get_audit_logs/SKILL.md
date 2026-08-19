---
name: vdr-get-audit-logs
description: Get VDR audit logs. Use when the user wants audit events for a data room or date range and the agent needs the VDR skill instructions or the runtime script at skills/vdr/get_audit_logs/scripts/get_audit_logs.py.
---

# Get audit logs

This file is an executable leaf skill entrypoint.

## Runtime entrypoint
- Execute `skills/vdr/get_audit_logs/scripts/get_audit_logs.py`.
- Do not search for another child skill under this directory.

Run the VDR audit-log script via the restricted command-style exec surface:

```text
python skills/vdr/get_audit_logs/scripts/get_audit_logs.py [--page <optional number>] [--size <optional number>] [--data-room "<optional string>"] [--start-date <optional YYYY-MM-DD>] [--end-date <optional YYYY-MM-DD>]
```

If all filters are omitted, run the script without extra flags.

Rules:
- Use CLI flags for normal execution; the final JSON-object tail exists only as temporary compatibility.
- `page` and `size` are optional positive integers when pagination is needed.
- `dataRoom` is an optional room identifier or room name filter when the user scopes audit events to one room.
- `startDate` and `endDate` are optional ISO calendar dates in `YYYY-MM-DD` format.
- Omit unused optional fields instead of sending placeholder values.
- Do not invent audit events, room identifiers, or timestamps; rely on tool output.
- Do not mention internal tool names in the user-facing reply.
