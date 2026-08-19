---
name: timeoff-submit-my-leave-request
description: Submit a leave request after collecting dates and a concrete time-off type ID. Use when the user asks to create, submit, book, or file a leave request for themselves.
---

# Submit My Leave Request

Use this leaf when the user is ready to submit a leave request.

# Intent Map

## Intent: submit-self-leave-request
### User request patterns
- create a leave request
- submit leave from 2026-04-10 to 2026-04-12
- request annual leave for next week
- take a day off next Friday
- submit an Annual Leave request for next Friday
- use Annual Leave for my pending leave request
- confirm and submit my Annual Leave request
- yes, submit the leave request with the selected leave type
- book a full day of leave for myself
- book PTO
- file a sick leave request
- take sick leave tomorrow
- submit my Sick Leave request for the selected dates
- confirm and use Sick Leave for this request
- request unpaid leave for next Friday
- submit an Unpaid Leave request for a full day
- confirm and use Unpaid Leave for this request

### Retrieval tags
- timeoff
- leave-request
- submit
- pto

### Answer objective
Collect or validate the leave-request inputs, then submit a leave request for the user with confirmed dates and a concrete time-off type ID.

### Instructions
- Confirm the exact `start_date` and `end_date` in `YYYY-MM-DD` format.
- Determine `day_type` from the user's wording:
  - Use `MORNING` when the user explicitly requests the morning or first half of the day.
  - Use `AFTERNOON` when the user explicitly requests the afternoon or second half of the day.
  - If the user only says "half day" or "nửa buổi" without specifying morning or afternoon, ask which half before submission.
  - Use `FULL_DAY` when the user does not mention a half day, morning, or afternoon.
- Require a concrete `time_off_type_id` before execution.
- If the user gave only a leave-type name and not a concrete ID, run this exact helper command first and keep the matching type name and ID visible: `python skills/timeoff/get_timeoff_types/scripts/get_timeoff_types.py`.
- If balance availability matters, the user asks whether they have enough leave, or the chosen leave type is balance-limited, run this exact helper command first before submission: `python skills/timeoff/get_my_leave_balances_and_types/scripts/get_my_leave_balances_and_types.py`.
- When checking balance, use the helper's `requestable_balance`, not only `available_balance`, because advance leave can allow a configured negative balance.
- If the helper output leaves multiple plausible type IDs, ask the user to confirm the exact leave type before continuing.
- Treat submission as a write action.
- **Mandatory User Confirmation & Turn Boundary**:
  - Before executing `submit_my_leave_request.py`, **ALWAYS** present a preview:
    - **Leave Type**: `<leave type name>`
    - **Dates**: `<start_date> to <end_date>`
    - **Day Type**: `<FULL_DAY, MORNING, or AFTERNOON>`
    - **Notes / Reason**: `<notes or "None">`
  - Ask the user: *"Do you confirm submitting this leave request?"*.
  - **STOP and wait for explicit user confirmation** (e.g. "yes", "confirm", "nộp đơn") in a subsequent turn before executing. **DO NOT execute the script in the same turn as presenting the preview.**
- Use the preferred execution command once inputs are complete.

### Required arguments
- `start_date` — required start date in `YYYY-MM-DD`.
- `end_date` — required end date in `YYYY-MM-DD`.
- `time_off_type_id` — required time-off type ID.
- `day_type` — optional `FULL_DAY`, `MORNING`, or `AFTERNOON`; defaults to `FULL_DAY`.
- `notes` — optional note.

### Execution
- Preferred execution: `exec` with `python skills/timeoff/submit_my_leave_request/scripts/submit_my_leave_request.py --start-date YYYY-MM-DD --end-date YYYY-MM-DD --time-off-type-id <id> [--day-type FULL_DAY|MORNING|AFTERNOON] [--notes text]`.
