---
name: utils-resolve-date-range
description: Resolve a strict date-range DSL into ISO start/end dates. Use when a date phrase has already been normalized into the supported DSL and the agent should execute skills/utils/resolve_date_range/scripts/resolve_date_range.py.
---

# Resolve date range

This file is an executable leaf skill entrypoint.

## Runtime entrypoint
- Execute `skills/utils/resolve_date_range/scripts/resolve_date_range.py`.
- Do not search for another child skill under this directory.

Run the utils script via the restricted command-style exec surface:

```text
python skills/utils/resolve_date_range/scripts/resolve_date_range.py --expression "<required DSL expression>" [--reference-date <optional YYYY-MM-DD>] [--use-reference-year-for-relative <optional true|false>]
```

Rules:
- `expression` must already be normalized to one supported DSL expression.
- Never invent concrete ISO dates before running the script.
- Use `startDate` and `endDate` from tool output as the final date range.
- Do not mention internal tool names in the user-facing reply.
