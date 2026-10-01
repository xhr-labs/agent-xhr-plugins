---
name: combine-check-task-timeoff-overlap
description: Check whether Workbench tasks, project assignments, due dates, or deadlines overlap with approved Timeoff leave. Use when the user asks about availability, leave overlap, deadline risk from time off, or whether a person or project team is on leave during task windows.
---

# Check Task Timeoff Overlap

Use this workflow leaf when the answer requires combining Workbench task/project data with Timeoff leave data.

# Intent Map

## Intent: check-task-timeoff-overlap
### User request patterns
- Who’s on leave during the Product Launch project?
- Do any Workbench Improvement tasks overlap with someone’s time off?
- Will Kadek be available when QA Testing is due?
- Which tasks might be delayed next week because of time off?
- Summarize which deadlines overlap with leaves.
- Are my tasks overlapping with my time off?

### Retrieval tags
- combine
- workbench
- timeoff
- overlap
- availability
- deadline-risk

### Answer objective
Return a grounded overlap or availability summary by combining Workbench task/project assignment data with approved Timeoff leave data.

### Instructions
- Treat this as a cross-domain workflow, not a single API lookup.
- Follow this workflow order strictly:
  1. fetch approved leave requests first
  2. fetch Workbench tasks second
  3. compare task due dates against leave ranges last
- Default the leave-request window to `from_date=today` and `to_date=end of next year` unless the user explicitly asks for a different window.
- Step 1: fetch leave requests first with `status=APPROVED`.
- If the user's wording is personal, such as `I`, `my`, `my tasks`, `my leave`, or another clearly self-referential phrasing, treat the employee scope as the current user.
- In that case, use `--mine true` for both the Timeoff leave lookup and the Workbench task lookup instead of resolving or passing another employee id.
- If the user mentions another employee by name, first resolve that employee by running `python skills/employee/search_employees/scripts/search_employees.py --name "<required name or keyword>"` and keep the resolved `employee_id` visible.
- If another employee was resolved in the previous step, pass that employee ID into the leave lookup with `--employee-id <employee-id>` so you only fetch that employee's approved leave requests.
- For leave lookup in this workflow, prefer `--recursive true` so the overlap check can reason over the full approved-leave set in scope.
- You do not need the user to explicitly mention recursion for this combine workflow; use `recursive=true` whenever the overlap decision depends on seeing the complete result set.
- Use recursive leave fetching such as `python skills/timeoff/get_leave_request/scripts/get_leave_request.py --status APPROVED --from-date <today> --to-date <end-of-next-year> --recursive true`.
- If the question is about the current user's own leave, use this leave command instead: `python skills/timeoff/get_leave_request/scripts/get_leave_request.py --mine true --status APPROVED --from-date <today> --to-date <end-of-next-year> --recursive true`.
- If the user mentioned another specific employee, use this leave command instead: `python skills/timeoff/get_leave_request/scripts/get_leave_request.py --status APPROVED --from-date <today> --to-date <end-of-next-year> --employee-id <employee-id> --recursive true`.
- Step 2: fetch Workbench tasks with `include_completed=false`.
- If the user mentions a concrete project or space name, first resolve its `project_id` by running `python skills/workbench/show_project_overview/scripts/show_project_overview.py --recursive true --project-name "<project or space name>"` and keep the resolved `project_id` visible.
- If another employee was resolved earlier, use that same employee ID as the Workbench `assignee_id` filter.
- Fetch tasks with the narrowest valid filters you can support.
- In this workflow, only consider tasks that are not completed, so include `--include-completed false` in the Workbench task lookup.
- For task lookup in this workflow, prefer `--recursive true` whenever the overlap decision depends on seeing the full task set in scope.
- You do not need the user to explicitly mention recursion for this combine workflow; use `recursive=true` whenever the overlap decision depends on a complete task result set.
- The preferred task command is `python skills/workbench/get_tasks/scripts/get_tasks.py --include-completed false --recursive true` plus any supported filters such as `--project-id <project-id>` and `--assignee-id <employee-id>`.
- If the question is about the current user's own tasks, use `python skills/workbench/get_tasks/scripts/get_tasks.py --mine true --include-completed false --recursive true` so task lookup stays on the canonical helper.
- Step 3: compare the task `due_date` against each approved leave range and report only real overlaps.
- For project-team questions, only treat someone as part of the project if the Workbench task data shows they are actually assigned to relevant project tasks.
- For availability questions about one person and one task, compare that task's due date against that person's approved leave ranges.
- For deadline-risk summaries, compare each relevant task due date against approved leave ranges and report the overlapping tasks, employees, and dates.
- Keep the final answer specific: mention the task, employee, project, and leave dates that caused the overlap.
- If no overlap is found, say so clearly instead of implying uncertainty.
- Do not invent assignees, project membership, leave records, or dates.

### Workflow modes
- `project_team_leave_overlap` — identify project assignees who are on approved leave during project-relevant task windows.
- `task_assignee_availability` — check whether a specific person is available when a named task is due.
- `my_task_timeoff_overlap` — compare the caller's own tasks against the caller's approved leave.
- `deadline_leave_summary` — summarize tasks or deadlines that overlap approved leave within a requested window.

### Execution
- Employee lookup when needed: `python skills/employee/search_employees/scripts/search_employees.py --name "<employee name>"`
- Approved-leave lookup for all employees in scope: `python skills/timeoff/get_leave_request/scripts/get_leave_request.py --status APPROVED --from-date YYYY-MM-DD --to-date YYYY-MM-DD --recursive true`
- Approved-leave lookup for the current user: `python skills/timeoff/get_leave_request/scripts/get_leave_request.py --mine true --status APPROVED --from-date YYYY-MM-DD --to-date YYYY-MM-DD --recursive true`
- Approved-leave lookup for one resolved employee: `python skills/timeoff/get_leave_request/scripts/get_leave_request.py --status APPROVED --from-date YYYY-MM-DD --to-date YYYY-MM-DD --employee-id <employee-id> --recursive true`
- Project lookup when a project or space name is known: `python skills/workbench/show_project_overview/scripts/show_project_overview.py --project-name "<project or space name>"`
- Primary Workbench task lookup: `python skills/workbench/get_tasks/scripts/get_tasks.py --include-completed false --recursive true`
- Current-user task lookup: `python skills/workbench/get_tasks/scripts/get_tasks.py --mine true --include-completed false --recursive true`
- Project-scoped task lookup: `python skills/workbench/get_tasks/scripts/get_tasks.py --project-id <project-id> --include-completed false --recursive true`
- Employee-scoped task lookup: `python skills/workbench/get_tasks/scripts/get_tasks.py --assignee-id <employee-id> --include-completed false --recursive true`
- Project plus employee scoped task lookup: `python skills/workbench/get_tasks/scripts/get_tasks.py --project-id <project-id> --assignee-id <employee-id> --include-completed false --recursive true`
