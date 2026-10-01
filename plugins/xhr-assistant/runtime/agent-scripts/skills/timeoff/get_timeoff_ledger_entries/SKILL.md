---
name: get-timeoff-ledger-entries
description: Inspect the time-off balance ledger history, accrual transactions, manual adjustments, and deductions for an employee.
side_effect: read
---

# Get Time-Off Ledger Entries

## Intent: get-timeoff-ledger-entries
### User request patterns
- show leave balance history for employee
- view time off balance logs
- why was leave balance deducted?
- inspect accrual transactions

### Retrieval tags
- timeoff
- ledger-entries
- balance-history
- accrual-logs
- balance-audit

### Instructions
- `employee_id` is required (resolve via employee search if only name is known).
- Run `get_timeoff_ledger_entries.py` to inspect balance transaction logs.

### Required arguments
- `employee_id`: UUID of the employee.

### Optional arguments
- `time_off_type_id`: Filter by specific leave type UUID.

### Execution
```text
python skills/timeoff/get_timeoff_ledger_entries/scripts/get_timeoff_ledger_entries.py --employee-id <UUID> [--time-off-type-id <UUID>]
```
