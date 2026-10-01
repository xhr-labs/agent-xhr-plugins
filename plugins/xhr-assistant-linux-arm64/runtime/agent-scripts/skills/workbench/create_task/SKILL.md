---
name: workbench-create-task
description: Create a Workbench task through one unified flow that collects missing fields, resolves project IDs and valid task statuses, requires explicit confirmation before writing, and then executes the final task-creation command. Use when the user asks to create, add, open, file, or start a new Workbench task and the agent needs one reliable public skill instead of separate collect and action leaves.
---

# Create Task

Use this as the canonical public leaf for Workbench task creation.

## Intent: create-task
### User request patterns
- create a new task in Workbench
- start a Workbench task and ask me for anything missing
- add a task called Fix Login Flow
- open a task in project Alpha
- create this Workbench task now
- what information do you need to create a Workbench task?
- Help me create a task
- I want to create task
- create task
- Create a new task named
- log ticket on space

### Retrieval tags
- workbench
- task
- create
- write-action
- intake
- confirmation

### Answer objective
Collect the required task fields, resolve a valid project ID and task status UUID, confirm the final payload, then create the Workbench task.

### Instructions
- Treat this leaf as the only public task-creation workflow.
- Treat task creation as a write action. Never execute the write step without explicit user confirmation of the final fields.
- Follow this sequence strictly:
  1. Read the user's request and extract any already-provided values for `task_name`, `project_id`, `project_name`, `status`, `priority`, `assignee_id`, `assignee`, `start_date`, `end_date`, and `description`.
  2. Decide whether anything is still missing or ambiguous.
  3. Handle `project` explicitly:
     - If the user already provided a trusted `project_id`, carry it forward.
     - If the user only gave a project name, run `python skills/workbench/show_project_overview/scripts/show_project_overview.py --project-name "<project_name>"`.
     - Keep returned project candidates visible. If multiple projects match, ask the user to confirm which one to use before continuing.
  4. Handle `status` explicitly:
     - First run `python skills/workbench/get_task_status_meta/scripts/get_task_status_meta.py` when the task status is missing, informal, ambiguous, or not already a trusted UUID.
     - If the user already mentioned a status label or status name, find the matching `status_id` from the returned task status list and carry that `status_id` forward into the final create command.
     - If the user did not mention any status, show the returned task status list to the user and ask them to pick the status before continuing.
  5. Handle assignee resolution explicitly:
     - If the user already provided a trusted `assignee_id`, carry it forward.
     - If the user only gave an assignee name, run `python skills/employee/search_employees/scripts/search_employees.py --name "<assignee name>"` and keep candidate employees visible until the user confirms the intended person.
  6. Ask follow-up questions only for missing or ambiguous fields. Do not ask again for fields the user already gave clearly.
  7. Before any write, summarize the exact final values in user-friendly form. Include which optional fields are currently omitted.
  8. Ask for explicit confirmation such as `Confirm`, `Yes, create it`, or an equivalent clear approval.
  9. Only after confirmation, execute the create command from this leaf.
  10. Report the result clearly, including the created task response and the payload used.
- Required fields before execution:
  - `task_name`
  - `project_id` as a valid UUID
  - `status` as a valid UUID for a task status
- Optional fields:
  - `priority`
  - `assignee_id`
  - `start_date`
  - `end_date`
  - `description`
- Ask follow-up questions when:
  - `task_name` is missing
  - `project_id` is missing and only a project name is known or needed
  - `status` is missing, informal, or ambiguous
  - `assignee_id` is missing but the assignee name needs resolution
  - a date is present but unclear or not in `YYYY-MM-DD`
  - the user says "create it" but has not confirmed the final write payload yet
- Execute without more questions only when all required fields are already present, any optional fields are either present or intentionally omitted, and the user has explicitly confirmed the final payload.
- Do not guess a project ID, task status UUID, or assignee UUID from informal labels.
- Prefer the public wrapper command in this leaf for the final write step.

### Required arguments
- `task_name` - required task name.
- `project_id` - required project UUID.
- `status` - required task status UUID.

### Optional arguments
- `project_name` - optional project name used for lookup before a concrete project UUID is known.
- `priority` - optional task priority. Preferred values: `Low`, `Medium`, `High`, `Urgent`.
- `assignee_id` - optional assignee employee UUID.
- `assignee` - optional assignee name used for lookup before a concrete employee UUID is known.
- `start_date` - optional `YYYY-MM-DD` task start date.
- `end_date` - optional `YYYY-MM-DD` task due date.
- `description` - optional task description.

### Execution
- Script entrypoint: `skills/workbench/create_task/scripts/create_task.py`
- Preferred final command:
  - `python skills/workbench/create_task/scripts/create_task.py --task-name "<task_name>" --project-id "<project_uuid>" --status "<status_uuid>"`
- Add optional flags only when values are confirmed:
  - `--priority "<Low|Medium|High|Urgent>"`
  - `--assignee-id "<employee_uuid>"`
  - `--start-date "<YYYY-MM-DD>"`
  - `--end-date "<YYYY-MM-DD>"`
  - `--description "<description>"`
- Example confirmed write command:
  - `python skills/workbench/create_task/scripts/create_task.py --task-name "Fix Login Flow" --project-id "22222222-2222-2222-2222-222222222222" --status "11111111-1111-1111-1111-111111111111" --priority "High" --assignee-id "33333333-3333-3333-3333-333333333333" --start-date "2026-04-06" --end-date "2026-04-08" --description "Stabilize the auth callback path"`
