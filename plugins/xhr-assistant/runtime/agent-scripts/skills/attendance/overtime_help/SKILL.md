---
name: attendance-overtime-help
description: Explain Attendance overtime setup and overtime calculation modes. Use when the user asks about overtime policies, overtime breakdown, retroactive overtime, or shift overtime configuration.
---

# Overtime Help

## Intent: attendance-overtime-help
### User request patterns
- explain overtime calculation
- configure overtime for a shift
- view overtime breakdown
- apply retroactive overtime
- create an overtime policy
- why is overtime missing
- why is overtime capped
- why is overtime negative
- why can I not change an overtime policy

### Retrieval tags
- attendance
- overtime
- shifts
- overtime-policy
- conditional-setup
- troubleshooting
- overtime-cap
- balance
- direct-answer

### Answer objective
Explain overtime policy behavior and where detailed executable setup belongs.

### Instructions
- Answer directly for help questions.
- Use `generate_overtime_policy` only when the user asks Lumi to draft an overtime policy setup.

### Direct answer
Open [Overtime Policies]({{attendance_overtime_policies_url}}) to create or manage overtime rules. Use [Shifts]({{attendance_shifts_url}}) to enable overtime for a shift and select its policy.

Overtime setup is optional. Do not create an overtime policy if the organization does not need overtime calculations. Attendance Tracking supports overtime configuration through an overtime policy assigned to a shift. Overtime calculation mode determines how extra time is calculated and displayed in attendance summaries or reports.

In Approved reports, Overtime Hours is the signed net balance; in Waiting for approval reports, it is projected recognized overtime. A negative balance represents undertime. Cap warnings mean recognized overtime was reduced, while cap-blocked results mean no overtime was recognized because the cap was already reached. If an assigned policy cannot be edited, create a new policy and assign it for future dates. Where supported, users can review overtime breakdowns and apply retroactive overtime behavior for shifts. Exact results depend on the shift target, policy settings, attendance sessions, effective dates, and backend calculation rules.
