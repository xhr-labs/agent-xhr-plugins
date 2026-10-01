---
name: workbench-sprint-planning-help
description: Explain Workbench sprint planning. Use when the user asks about creating, editing, starting, completing, deleting sprints, or moving unfinished tasks.
---

# Sprint Planning Help

## Intent: workbench-sprint-planning-help
### User request patterns
- create a sprint
- start a sprint
- complete a sprint
- move unfinished sprint tasks
- explain sprint planning in Workbench
- explain why a Contributor cannot create a sprint

### Retrieval tags
- workbench
- sprints
- sprint-planning
- unfinished-tasks
- direct-answer

### Answer objective
Explain sprint lifecycle behavior at a product level.

### Instructions
- Answer directly without calling executable tools.

### Direct answer
Open [Workbench -> Spaces]({{workbench_spaces_url}}) and select the project.

Workbench sprint planning supports a sprint lifecycle for project teams. The current UI allows the space Owner to manage sprints when sprint planning is enabled for the space. Contributor and Viewer sharing roles do not grant sprint management. Do not tell users to assign Owner through Share: that dropdown only offers Contributor and Viewer. Ask the existing Owner to manage the sprint; for ownership-delegation questions, use `skills/workbench/share_and_permissions/SKILL.md`.

When completing a sprint, unfinished tasks may need to be moved to another planned sprint or returned to the backlog. This keeps active sprint scope accurate while preserving unfinished work.
