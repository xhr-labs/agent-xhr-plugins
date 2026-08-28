---
name: skills-root
description: Root navigation catalog for locating the correct X-HR skill domain and executable leaf, especially when the user's latest request is outside a client-selected context. Read this index before changing domains; never execute from the root.
---

# Skills root index

Use this file as the primary domain-discovery entrypoint for the skill tree. It gives the agent a small, stable catalog for finding the correct domain index without loading every leaf skill into the prompt.

## Navigation contract
- This file is an index only.
- Use the user's latest explicit intent to choose exactly one best-matching domain entrypoint whenever possible.
- Start here when no retrieved or selected leaf covers the latest request, including when the client-selected context belongs to a different domain.
- A client-selected skill remains primary while the latest request is still within its scope. A clear cross-domain request must be routed through this catalog instead of being forced into the selected skill.
- To navigate deeper, read the chosen domain `SKILL.md`, then read the smallest sufficient child leaf `SKILL.md` before answering or executing.
- Treat domain descriptions as routing hints, not as permission to invent a leaf path, script path, command, or arguments.
- If two domains remain genuinely plausible after reading their indexes, ask one focused clarification question instead of guessing.
- Do not execute this file or this directory as a script skill.
- Execute only scripts that are explicitly declared by a leaf `SKILL.md`.

## Child entrypoints
- skills/allocation_management/SKILL.md — Plan project allocations; review utilization, allocation dashboards, timesheet variance, and resource or project allocation reports.
- skills/appstore/SKILL.md — Install, remove, manage, or build X-HR apps and answer App Store marketplace questions.
- skills/asset_inventory/SKILL.md — Find or manage employee assets, requests, approvals, lifecycle records, vendors, categories, bundles, and register exports.
- skills/attendance/SKILL.md — Handle attendance, shifts, timesheets, approvals, overtime policies, and attendance reporting.
- skills/calendar/SKILL.md — Book appointments or meetings, manage share links and Google Calendar integration, and work with public-holiday calendars.
- skills/combine/SKILL.md — Use only for workflows that explicitly require coordinated actions or checks across multiple X-HR domains.
- skills/company/SKILL.md — Find or manage company profile data, organization structure, departments, statistics, and work locations.
- skills/document_generator/SKILL.md — Generate employee documents from DOCX templates, merge employee data, preview versions, and export DOCX or PDF files.
- skills/documents/SKILL.md — List, search, access, store, and explain authorized company documents and document-management behavior.
- skills/compensation_benefits/SKILL.md — Handle reward elements, compensation packages, component setup, benefits, and payroll-integration guidance.
- skills/employee/SKILL.md — Find employee profiles and managers or handle employee lifecycle, organization, reporting, and profile actions.
- skills/employment_records/SKILL.md — Handle employment contracts, employee changes, attachments, activity logs, company decisions, and record permissions.
- skills/final_settlement/SKILL.md — Explain end-of-employment final-settlement setup, process, access, and permissions.
- skills/finance_hub/SKILL.md — Review financial dashboards, income and expenses, categories, burn rate, runway, currencies, and finance reports.
- skills/forms/SKILL.md — Create, publish, secure, version, review, and manage forms, submissions, review forms, and onboarding forms.
- skills/greeting/SKILL.md — Answer greetings and questions about the assistant's identity or name.
- skills/helpdesk/SKILL.md — Answer general X-HR how-to, setup, billing, compliance, mobile, Lumi AI, support, and integration questions.
- skills/language/SKILL.md — Check supported languages or change the user's X-HR interface language.
- skills/payroll/SKILL.md — Configure payroll and pay components or handle earnings, payslips, pay runs, tax, proration, compliance, and statutory schemes.
- skills/support_ticket/SKILL.md — Collect details and submit an X-HR support request or product feature request.
- skills/timeoff/SKILL.md — Check leave balances and types; plan, submit, approve, cancel, or review leave requests; configure time-off policies and carry-over.
- skills/utils/SKILL.md — Resolve dates and run other shared, low-risk utility operations required by executable domain leaves.
- skills/vdr/SKILL.md — Manage Virtual Data Rooms, files, sharing, access requests, stakeholders, activity analytics, and audit logs.
- skills/workbench/SKILL.md — Find or manage Workbench projects, tasks, priorities, statuses, pages, wiki content, dashboards, and project overviews.
- skills/workflow/SKILL.md — Build and manage workflows, approvals, Task Hub tasks, form tasks, triggers, actions, and date-based automation.
