---
name: workbench-create-task-from-wiki
description: Draft and create a Workbench task from company wiki, project wiki, or space wiki content by resolving the correct wiki page, fetching its content, extracting grounded task fields, resolving any remaining project/status/assignee identifiers, and requiring explicit confirmation before the final write action. Use when the user asks to turn a wiki page, wiki content, or documentation into a task draft or a new Workbench task.
---

# Create Task From Wiki

Use this workflow leaf when the user explicitly wants to turn wiki content into a task draft or into a final Workbench task.

# Intent Map

## Intent: draft-task-from-wiki
### User request patterns
- create a task from this wiki page
- turn this wiki article into a task
- draft a Workbench task from this documentation
- use the wiki page to prepare a task
- make a task draft from this page
- create a task from the space wiki
- use this project wiki page to draft a task
- turn this company wiki page into a task draft
- create a task from the wiki in space Platform Cleanup
- make a Workbench task from the company wiki page about onboarding
- set up tickets for the actionables that have the priority = P1
- set up tickets from wiki page

### Retrieval tags
- workbench
- task
- wiki
- draft
- create
- company-wiki
- project-wiki
- space-wiki

### Answer objective
Resolve the correct wiki page, use its content to prepare grounded task fields, then complete the Workbench task-creation flow without skipping explicit user confirmation before the final write action.

### Instructions
- Treat this as a workflow leaf, not an executable leaf.
- Follow this sequence strictly:
  1. search for the relevant wiki/document content
  2. extract or propose task fields from the returned content
  3. resolve any missing project, status, or assignee identifiers
  4. summarize the final task payload
  5. require explicit confirmation before the final task-creation write
- Keep resolved wiki/document hits and task-creation identifiers visible so follow-up steps stay grounded.
- Do not invent wiki content, task status UUIDs, project UUIDs, or assignee UUIDs.

## Step 1: search for the relevant wiki/document content
- Run the document search tool with the user's query:
  - `SearchDocuments {"query": "<user query>"}`
- Use the returned wiki/document results as the source material for the next drafting step.
- If the search query is too vague, ask a short clarification question before running the search.
- If multiple relevant results are returned, keep them visible and ask the user to confirm which result should be used as the task source.
- If no matching result is found, say so clearly and ask the user to refine the query.

## Step 2: derive task draft inputs from the wiki content
- Once the wiki content is available, summarize the relevant task-drafting inputs you can extract from it, such as:
  - `task_name`
  - `description`
  - `project_id` or `project_name`
  - possible priority
  - possible dates
  - possible assignee name
  - acceptance criteria or implementation notes
- Be explicit about which values came directly from the wiki and which values are still missing or are only suggestions.
- If the wiki content is broad, ambiguous, or contains multiple action items, ask the user which action item should become the task.
- Present a concise task draft before moving into the final create flow.

## Step 3: resolve remaining task fields
### Project
- If a trusted `project_id` already exists from the wiki path, carry it forward.
- If the task still needs a project and only a project name is known, run:
  - `python skills/workbench/show_project_overview/scripts/show_project_overview.py --project-name "<project or space name>"`
- If multiple projects match, ask the user to confirm which project to use before continuing.

### Status
- If no trusted task status UUID is present, run:
  - `python skills/workbench/get_task_status_meta/scripts/get_task_status_meta.py`
- If the user already mentioned a status label or status name, map it to a valid `status_id` from the returned task status list.
- If the user did not mention any status, show the valid task statuses and ask the user to pick one before continuing.

### Assignee
- If a trusted `assignee_id` already exists, carry it forward.
- If only an assignee name is known, run:
  - `python skills/employee/search_employees/scripts/search_employees.py --name "<assignee name>"`
- Keep candidate employees visible until the user confirms the intended assignee.

### Remaining fields
- Ask follow-up questions only for missing or ambiguous fields such as:
  - `task_name`
  - `project_id`
  - `status`
  - `assignee_id`
  - dates not in `YYYY-MM-DD`
  - description or scope that is still unclear
- Do not ask again for fields the user already gave clearly.

## Step 4: confirm before writing
- Treat the final create step as a write action.
- Before any write, summarize the exact final values in user-friendly form, including omitted optional fields.
- Ask for explicit confirmation such as `Confirm`, `Yes, create it`, or another clearly affirmative approval.
- If the user only asked for a draft, stop after showing the draft and do not continue into the final create step.
- Do not execute the final task creation step until the user clearly approves the final payload.

## Step 5: final execution
- Only after explicit confirmation, execute the final Workbench task creation command.
- Preferred final command:
  - `python skills/workbench/create_task/scripts/create_task.py --task-name "<task_name>" --project-id "<project_uuid>" --status "<status_uuid>"`
- Add optional flags only when values are confirmed:
  - `--priority "<Low|Medium|High|Urgent>"`
  - `--assignee-id "<employee_uuid>"`
  - `--start-date "<YYYY-MM-DD>"`
  - `--end-date "<YYYY-MM-DD>"`
  - `--description "<description>"`

### Execution
- Document search:
  - `SearchDocuments {"query": "<user query>"}`
- Project lookup:
  - `python skills/workbench/show_project_overview/scripts/show_project_overview.py --project-name "<project or space name>"`
- Status lookup:
  - `python skills/workbench/get_task_status_meta/scripts/get_task_status_meta.py`
- Employee lookup:
  - `python skills/employee/search_employees/scripts/search_employees.py --name "<assignee name>"`
- Final task creation:
  - `python skills/workbench/create_task/scripts/create_task.py --task-name "<task_name>" --project-id "<project_uuid>" --status "<status_uuid>"`
