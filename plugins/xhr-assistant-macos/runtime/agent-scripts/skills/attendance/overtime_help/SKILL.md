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

### Retrieval tags
- attendance
- overtime
- shifts
- overtime-policy
- direct-answer

### Answer objective
Explain overtime policy behavior and where detailed executable setup belongs.

### Instructions
- Answer directly for help questions.
- Use `generate_overtime_policy` only when the user asks Lumi to draft an overtime policy setup.

### Direct answer
Open [Attendance Configuration]({{attendance_configuration_url}}) to manage overtime settings.

Attendance Tracking supports overtime configuration through shift or overtime policy setup. Overtime calculation mode determines how extra time is calculated and displayed in attendance summaries or reports.

Where supported, users can review overtime breakdowns and apply retroactive overtime behavior for shifts. Exact results depend on the shift target, policy settings, attendance sessions, and backend calculation rules.
