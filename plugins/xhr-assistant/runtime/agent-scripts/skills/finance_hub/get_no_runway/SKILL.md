---
name: finance-hub-get-no-runway
description: Get Finance Hub runway reporting from current metrics. Use when the user wants runway, cash-burn projection, or current runway context and the agent should execute skills/finance_hub/get_no_runway/scripts/get_no_runway.py.
---

# Get runway

This file is an executable leaf skill entrypoint.

## Runtime entrypoint
- Execute `skills/finance_hub/get_no_runway/scripts/get_no_runway.py`.
- Do not search for another child skill under this directory.

## Intent Map

### User request patterns
- How many months of runway do I have with my current cash?
- How many months of runway do I have?

### Retrieval tags
- finance-hub
- runway
- cash-burn
- analytics

### Answer objective
Run the current-runway reporting leaf for runway questions about how many months of runway remain with current cash and burn.

### Instructions
- This report currently takes no user-supplied CLI flags.
- This report is admin-scoped; rely on tool output for permission denials instead of guessing access.
- Do not invent runway months, net-income totals, or chart values; rely on tool output.
- Do not mention internal tool names in the user-facing reply.
- Use this leaf for runway questions about how many months of runway remain with current cash and burn.
- Execute it directly and rely on tool output.

### Execution
```text
python skills/finance_hub/get_no_runway/scripts/get_no_runway.py
```
