---
name: vdr-aggregate-audit-logs
description: Aggregate VDR audit logs. Use when the user wants summarized or grouped VDR audit activity over a date range or for a data room and the agent needs the VDR skill instructions or the runtime script at skills/vdr/aggregate_audit_logs/scripts/aggregate_audit_logs.py.
---

# Aggregate audit logs

This file is an executable leaf skill entrypoint.

## Runtime entrypoint
- Execute `skills/vdr/aggregate_audit_logs/scripts/aggregate_audit_logs.py`.
- Do not search for another child skill under this directory.

## Intent Map

### User request patterns
- Who accessed our documents in the last 7 days, and what did they view?
- Who accessed our virtual data room in the last 7 days, and what did they view?
- summarize VDR audit activity
- group audit log activity by viewer and file
- show aggregated document access activity

### Retrieval tags
- vdr
- audit-logs
- aggregate
- data-room
- document-access

### Answer objective
Return grouped VDR audit activity over a date range or for a data room without inventing counts, actors, or accessed files.

### Instructions
- Use CLI flags for normal execution; the final JSON-object tail exists only as temporary compatibility.
- `dataRoom` is an optional room identifier or room name filter when the user scopes aggregation to one room.
- `startDate` and `endDate` are optional ISO calendar dates in `YYYY-MM-DD` format.
- Omit unused optional fields instead of sending placeholder values.
- Do not invent aggregate counts, actors, or timestamps; rely on tool output.
- Do not mention internal tool names in the user-facing reply.

### Execution
```text
python skills/vdr/aggregate_audit_logs/scripts/aggregate_audit_logs.py [--data-room "<optional string>"] [--start-date <optional YYYY-MM-DD>] [--end-date <optional YYYY-MM-DD>]
```

If all filters are omitted, run the script without extra flags.
