---
name: workbench-show-my-highest-priority-task
description: Show the caller's highest-priority Workbench task. Use when the user asks for their top priority, most important task, or what they should focus on next in Workbench.
---

# Show My Highest Priority Task

Use this executable leaf when the user wants the single highest-priority task assigned to them.

# Intent Map

## Intent: show-my-top-priority-task
### User request patterns
- what's my highest priority task?
- show my top task
- what should I focus on next in Workbench?
- show my most important assigned task
- get my highest priority work item
- which of my tasks have the highest priority?

### Retrieval tags
- workbench
- task
- priority
- mine

### Answer objective
Return the caller's highest-priority Workbench task so they can immediately see the top item to focus on.

### Instructions
- Use this leaf when the user wants one top-priority item rather than a full task list.
- If the user instead wants multiple tasks or additional filtering, do not use this leaf.
- Read `skills/workbench/get_tasks/SKILL.md` and follow that leaf instead.
- Preserve the underlying helper's paging argument if the runtime supports it.
- Use the executable leaf rather than inventing task priority data.

### Supported arguments
- `page_number` — optional page number when the underlying helper supports paging.

### Execution
- Script entrypoint: `skills/workbench/show_my_highest_priority_task/scripts/show_my_highest_priority_task.py`
- Use the restricted command-style `exec` surface with the explicit runtime-relative wrapper path and CLI flags when available.
