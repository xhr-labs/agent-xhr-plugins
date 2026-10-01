---
name: workflow-trigger-timeoff-created
description: Leaf guide for the `time_off.created` workflow trigger and its available condition variables.
---

# Time Off Created Trigger

Event key: `time_off.created`

This trigger fires when a new time off request is created.

## Available Variables for Gateway Conditions
- `days` — integer request day count; supported comparisons: `>`, `<`, `==`, `!=`, `>=`, `<=`
- `requester_id` — compare with `==` or `!=`
- `leave_type` — compare with `==` or `!=`

## Helper dependencies
- If the user provides a requester name, resolve it with the employee search skill.
