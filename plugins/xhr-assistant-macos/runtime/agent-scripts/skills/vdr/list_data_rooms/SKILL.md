---
name: vdr-list-data-rooms
description: List VDR data rooms. Use when the user wants to browse or search data rooms and the agent needs the VDR skill instructions or the runtime script at skills/vdr/list_data_rooms/scripts/list_data_rooms.py.
---

# List data rooms

This file is an executable leaf skill entrypoint.

## Runtime entrypoint
- Execute `skills/vdr/list_data_rooms/scripts/list_data_rooms.py`.
- Do not search for another child skill under this directory.

Run the VDR list-data-rooms script via the restricted command-style exec surface:

```text
python skills/vdr/list_data_rooms/scripts/list_data_rooms.py [--page <optional number>] [--size <optional number>] [--name "<optional string>"]
```

If all filters are omitted, run the script without any extra flags.

Rules:
- `page` and `size` are optional positive integers when pagination is needed.
- `name` is an optional plain-text filter for the room name.
- Omit unused optional fields instead of sending placeholder values.
- Do not invent room IDs, counts, or metadata; rely on tool output.
- Do not mention internal tool names in the user-facing reply.
