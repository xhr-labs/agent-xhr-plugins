---
name: allocation-management-monthly-allocations-help
description: Explain monthly allocation lists in Allocation Management. Use when the user asks about allocation rows, allocation percent, period lock, utilization warnings, or adding project allocation rows.
---

# Monthly Allocations Help

## Intent: allocation-management-monthly-allocations-help
### User request patterns
- add monthly allocation rows
- edit allocation percent
- lock an allocation month
- explain utilization warnings
- plan employee allocation for a project
- explain why an employee cannot be allocated
- copy an allocation to another month
- explain allocation status or warning colors
- explain how allocation percentage is calculated
- explain MM or man-months in the Allocation table
- explain MD or man-days in the Allocation table

### Retrieval tags
- allocation-management
- monthly-allocations
- allocation-percent
- man-months
- man-days
- period-lock
- utilization
- employee-eligibility
- direct-answer

### Answer objective
Explain the monthly allocation planning workflow, calculations, validation rules, and guarded edit behavior.

### Instructions
- Answer directly without calling executable tools.
- Use the selected month as the planning context. A row may cover a date range across several months, and each month is calculated separately.
- Explain that allocation percentage must be greater than 0 and no higher than 100. The system calculates effort from the employee's working days after public holidays and eligible approved unpaid or maternity leave.
- Explain that `% allocation` in the table is the user's planning input. It is not calculated from FTE, MM, or MD, and it is not the same as utilization. It represents the share of a standard working day assigned to that project during the selected date range.
- Explain the calculation in plain language: available working days in the allocation date range multiplied by `% allocation` divided by 100 gives MD. The service calculates each month separately, then adds the monthly results for a row spanning multiple months.
- Explain `MD` or man-days as planned effort measured in working days. Example: a full month at 50% produces about half of that month's available working days as MD; the exact value depends on work location, holidays, and approved leave.
- Explain `MM` or man-months as planned effort normalized against the month's working days. A full month at 100% is approximately 1 MM; a partial date range, lower percentage, holiday, or leave reduces the MM. MM and MD can differ because MD is a day total while MM is a month-normalized value.
- Explain that FTE does not multiply the row's MD/MM calculation. FTE defines the employee's available capacity, so it affects utilization and over/under-allocation warnings.
- When users ask about a table warning, explain that the system compares the employee's total allocation MM for the month with the employee's capacity MM. This is different from the row's `% allocation` input.
- Explain that an employee must be active, production-enabled, have a resolved FTE greater than zero, and be capacity-counted before a new allocation can be saved. A search result can still be visible even when it is not eligible to save.
- Explain the FTE order as employee Job Details value, then Employee Type default, then no usable FTE. Do not expose internal field or endpoint names unless the user is explicitly troubleshooting setup.
- Explain that the same employee cannot have overlapping date ranges on the same project. Adjacent ranges are allowed. A closed project cannot receive a new allocation.
- Explain that a locked month blocks creating, editing, or deleting allocations that touch that month. If an edit spans months, every affected month must be open.
- Explain statuses as planning labels: Planned, Tentative, and Unverified. They describe confidence or verification; they do not bypass validation or period locks.
- Tell users to use Preview before saving when available. Preview shows the effect on employee/project totals and may flag over-allocation; it does not unlock a locked period.
- Explain that current employee names may update from the employee profile while prior allocation calculations continue to reflect the project, department, FTE, and capacity information used for that plan.
- Keep notes plain and concise. Unsafe markup is removed and an empty note is treated as no note.

### Direct answer
Open [Monthly Allocations]({{allocation_url}}).

Monthly allocations let authorized users plan employee effort by project, role, date range, allocation percentage, status, and notes. The list can include saved rows and inline draft rows before they are saved.

In the table, `% allocation` is the plan input, `MD` is planned effort in working days, and `MM` is the same effort normalized to a working month. These values are calculated from the allocation dates and the employee's working calendar. They are not a timesheet actual.

Users with allocation write permission can add, edit, copy, or remove rows when the selected month and project state allow it. Period locking prevents further changes for a closed planning month. Utilization warnings help identify over- or under-allocation against capacity; they are planning signals, not automatic approvals or rejections.

When a save fails, check in this order: employee eligibility and resolved FTE, project status and access, overlapping dates, the selected month lock, then the user's allocation or project write permission.
