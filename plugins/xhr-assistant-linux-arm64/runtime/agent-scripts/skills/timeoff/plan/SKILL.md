---
name: timeoff-plan
description: Generate time-off plan suggestions around holidays and leave budgets. Use when the user asks for vacation planning, maximizing consecutive days off, or finding good leave windows.
---

# Plan Time Off

Use this leaf when the user wants help planning vacation windows or maximizing days off around holidays.

# Intent Map

## Intent: generate-time-off-plan
### User request patterns
- Plan the best upcoming vacation for me
- Find the best upcoming time off with minimal leave days.
- When should I take leave to get the longest break?
- Suggest the smartest dates for my next vacation.
- Plan the best New Year holiday for me, with a total of x days off

### Retrieval tags
- timeoff
- planning
- holiday
- optimization

### Answer objective
Return helper-backed time-off plan suggestions that match the user's date window, holiday target, or leave budget without fabricating unsupported plans.

### Instructions
- Carry forward any explicit `from_date`, `to_date`, `year`, `max_leave_days`, `max_total_days`, or `holiday_name` constraints.
- If the user gave only a rough planning goal, infer the lightest safe set of helper arguments and keep assumptions explicit.
- Treat helper output as the source of truth.
- Do not invent plans when `candidatePlans` and `recommendedPlans` are both absent.
- If leave balance is likely relevant and unknown, consider using `skills/timeoff/get_my_leave_balances_and_types/SKILL.md` first.
- When advance leave is enabled, the helper can plan against available balance plus the configured advance-leave limit.

### Supported arguments
- `from_date` — optional start date in `YYYY-MM-DD`.
- `to_date` — optional end date in `YYYY-MM-DD`.
- `year` — optional year in `YYYY`.
- `max_leave_days` — optional leave-day budget.
- `max_total_days` — optional total-days-off target.
- `holiday_name` — optional holiday filter.

### Execution
- Preferred execution: `exec` with `python skills/timeoff/plan/scripts/plan.py [--from-date YYYY-MM-DD] [--to-date YYYY-MM-DD] [--year YYYY] [--max-leave-days N] [--max-total-days N] [--holiday-name text]`.
