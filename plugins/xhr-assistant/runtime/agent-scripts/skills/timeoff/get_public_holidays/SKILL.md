---
name: get-public-holidays
description: List company public holidays and official non-working days for a given year or date range.
side_effect: read
---

# Get Public Holidays

## Intent: get-public-holidays
### User request patterns
- show public holidays this year
- when is the next holiday?
- list company holidays for 2026

### Retrieval tags
- timeoff
- public-holidays
- holidays
- non-working-days
- company-calendar

### Instructions
- Run `get_public_holidays.py` to fetch company public holidays.
- Defaults to the current calendar year if year is omitted.

### Optional arguments
- `year`: Calendar year (e.g. `2026`).
- `start_date`: Start date (`YYYY-MM-DD`).
- `end_date`: End date (`YYYY-MM-DD`).

### Execution
```text
python skills/timeoff/get_public_holidays/scripts/get_public_holidays.py [--year <YYYY>] [--start-date <YYYY-MM-DD>] [--end-date <YYYY-MM-DD>]
```
