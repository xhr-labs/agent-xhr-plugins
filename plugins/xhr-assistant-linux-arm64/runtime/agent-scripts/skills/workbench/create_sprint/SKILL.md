---
name: create-sprint
description: Create a new sprint in a Workbench project with goal, start date, and end date.
side_effect: write
---

# Create Sprint

## Intent: create-sprint
### User request patterns
- create new sprint
- plan next sprint
- add sprint to project

### Retrieval tags
- workbench
- create-sprint
- sprint-planning
- new-sprint
- agile

### Instructions
- **Disambiguation Rule (Enable Sprint vs Create Sprint)**:
  - If the user asks to **enable**, **turn on**, or **activate** sprints for a project (e.g. `enable sprint for this project ML, testing`), do NOT use `create_sprint`. Instead, read and execute `update-project` (`skills/workbench/update_project/SKILL.md`) with `--enable-sprint true`.
- **Input Verification Rule**:
  - `sprint_name` is required. Do NOT invent or guess default sprint names (e.g. 'Sprint 1') without explicit user confirmation.
  - If `project_id` or `sprint_name` is missing, ask the user to specify.
  - If dates are not provided, ask the user or propose default dates (e.g. 2 weeks) and ask for confirmation.
- **Mandatory User Confirmation & Turn Boundary**:
  - Before executing `create_sprint.py`, **ALWAYS** present a clear preview of the planned sprint:
    - **Project**: `<project name>`
    - **Sprint Name**: `<sprint name>`
    - **Goal**: `<goal or "None">`
    - **Start Date**: `<YYYY-MM-DD>`
    - **End Date**: `<YYYY-MM-DD>`
  - Ask the user: *"Do you confirm creating sprint '[Sprint Name]' in project '[Project Name]'?"*.
  - **STOP and wait for explicit user confirmation** (e.g. "yes", "confirm", "đồng ý") in a subsequent turn before executing. **DO NOT execute the script in the same turn as receiving inputs or showing the preview.**
- `project_id` is required and must be a valid UUID (if unknown, run `python skills/workbench/show_project_overview/scripts/show_project_overview.py [--project-name "<name>"]` to resolve `project_id`).
- `sprint_name` is required.
- `goal`, `start_date` (YYYY-MM-DD), `end_date` (YYYY-MM-DD), and `duration` (e.g. "2 weeks") are optional.

### Required arguments
- `project_id`: UUID of the project.
- `sprint_name`: Name/title of the new sprint.

### Optional arguments
- `goal`: Sprint goal description.
- `start_date`: Start date (`YYYY-MM-DD`).
- `end_date`: End date (`YYYY-MM-DD`).
- `duration`: Duration descriptor (e.g. "1 week", "2 weeks", "1 month").

### Execution
```text
python skills/workbench/create_sprint/scripts/create_sprint.py --project-id <UUID> --sprint-name "<name>" [--goal "<goal>"] [--start-date <YYYY-MM-DD>] [--end-date <YYYY-MM-DD>]
```
