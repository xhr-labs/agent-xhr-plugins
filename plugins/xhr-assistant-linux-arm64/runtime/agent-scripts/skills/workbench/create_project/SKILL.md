---
name: workbench-create-project
description: Create a Workbench project through one unified flow that collects missing fields, resolves valid project statuses, requires explicit confirmation before writing, and then executes the final project-creation command. Use when the user asks to create, start, open, add, or set up a new Workbench project and the agent needs one reliable public skill instead of separate collect and action leaves.
---

# Create Project

Use this as the canonical public leaf for Workbench project creation.

## Intent: create-project
### User request patterns
- create a new project in Workbench
- start a Workbench project and ask me for anything missing
- add a project called Alpha Launch
- set up a new Workbench space for the redesign effort
- create this Workbench project now
- what information do you need to create a Workbench project?
- Help me create a project
- I want to create space
- Help me create a space
- i want to create project
- Create a new project named
- create project

### Retrieval tags
- workbench
- project
- create
- write-action
- intake
- confirmation

### Answer objective
Collect the required project fields, resolve a valid status UUID, confirm the final payload, then create the Workbench project.

### Instructions
- Treat this leaf as the only public project-creation workflow.
- Treat project creation as a write action. Never execute the write step without explicit user confirmation of the final fields.
- Follow this sequence strictly:
  1. Read the user's request and extract any already-provided values for `project_name`, `description`, `start_date`, `due_date`, and `status`.
  2. Decide whether anything is still missing or ambiguous.
  3. Handle `status` explicitly:
     - First run `python skills/workbench/get_project_status_meta/scripts/get_project_status_meta.py`.
     - If the user already mentioned a status label or status name, find the matching `status_id` from the returned project status list and carry that `status_id` forward into the final create command.
     - If the user did not mention any status, show the returned project status list to the user and ask them to pick the status before continuing.
  4. Ask follow-up questions only for missing or ambiguous fields. Do not ask again for fields the user already gave clearly.
  5. Before any write, summarize the exact final values in user-friendly form. Include which fields are optional and currently omitted.
  6. Ask for explicit confirmation such as `Confirm`, `Yes, create it`, or an equivalent clear approval.
  7. Only after confirmation, execute the create command from this leaf.
  8. Report the result clearly, including the created project response and the payload used.
- Required fields before execution:
  - `project_name`
  - `status` as a valid UUID for a project status
- Optional fields:
  - `description`
  - `start_date`
  - `due_date`
  - `enable_sprint` (boolean: true/false)
- Ask follow-up questions when:
  - `project_name` is missing
  - `status` is missing, informal, or ambiguous
  - the user says "create it" but has not confirmed the final write payload yet
  - a date is present but unclear or not in `YYYY-MM-DD`
- Execute without more questions only when all required fields are already present, any optional fields are either present or intentionally omitted, and the user has explicitly confirmed the final payload.
- Do not guess a project status UUID from a label like `Planned`, `Doing`, or `On track`.
- First run `python skills/workbench/get_project_status_meta/scripts/get_project_status_meta.py`.
- If the user already gave a status label, match it against the returned project status list and carry the matching `status_id` into the final create command.
- If the user did not give any status, keep the returned `project_statuses` visible and ask the user to choose the status before continuing.
- Prefer the public wrapper command in this leaf for the final write step.

### Required arguments
- `project_name` - required project name.
- `status` - required project status UUID.

### Optional arguments
- `description` - optional project description.
- `start_date` - optional `YYYY-MM-DD` project start date.
- `due_date` - optional `YYYY-MM-DD` target due date.
- `enable_sprint` - optional boolean flag (`true` or `false`) to enable Sprint planning in the project.

### Execution
- Script entrypoint: `skills/workbench/create_project/scripts/create_project.py`
- Preferred final command:
  - `python skills/workbench/create_project/scripts/create_project.py --project-name "<project_name>" --status "<status_uuid>"`
- Add optional flags only when values are confirmed:
  - `--description "<description>"`
  - `--start-date "<YYYY-MM-DD>"`
  - `--due-date "<YYYY-MM-DD>"`
  - `--enable-sprint true|false`
- Example confirmed write command:
  - `python skills/workbench/create_project/scripts/create_project.py --project-name "Alpha Launch" --description "Launch planning workspace" --start-date "2026-04-06" --due-date "2026-05-15" --status "11111111-1111-1111-1111-111111111111" --enable-sprint true`
