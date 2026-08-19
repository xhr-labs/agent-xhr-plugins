---
name: calendar-get-public-holidays
description: Retrieve public holidays for the employee context. Use when the user asks for public holidays, holiday lists, or non-working public holiday dates and the agent needs the calendar skill instructions or the runtime script at skills/calendar/get_public_holidays/scripts/get_public_holidays.py.
---

# Get public holidays

This file is an executable leaf skill entrypoint.

## Runtime entrypoint
- Execute `skills/calendar/get_public_holidays/scripts/get_public_holidays.py`.
- Do not search for another child skill under this directory.

## Intent Map

### User request patterns
- show public holidays
- list public holidays this year
- get public holidays for 2026
- what are the public holidays for my location?
- show holiday dates
- How many public holidays in my region
- public holidays

### Retrieval tags
- calendar
- public-holidays
- holidays
- year
- list

### Answer objective
Return public holidays for the relevant employee context, optionally scoped to a requested year.

### Instructions
- If the user explicitly asks for a specific year, pass that year with `--year`.
- If the user does not specify a year, omit `--year` and let the helper use the default context.
- Use the tool output as the source of truth for holiday names and dates.
- Do not invent holiday data.
- Do not mention internal tool names in the user-facing reply.

### Supported arguments
- `year` — optional year filter in `YYYY` form.

### Execution
```text
python skills/calendar/get_public_holidays/scripts/get_public_holidays.py [--year <optional YYYY>]
```

If no year is needed, run the script without any extra flags:

```text
python skills/calendar/get_public_holidays/scripts/get_public_holidays.py
```
