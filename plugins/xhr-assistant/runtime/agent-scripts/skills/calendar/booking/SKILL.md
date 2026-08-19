---
name: calendar-booking
description: Book a calendar slot with a colleague by employee name or UUID. Use when the user wants to schedule or book time with someone and the agent needs the calendar booking skill instructions or the runtime script at skills/calendar/booking/scripts/booking.py.
side_effect: write
idempotency: none
---

# Calendar booking

This file is an executable leaf skill entrypoint.

## Runtime entrypoint
- Execute `skills/calendar/booking/scripts/booking.py`.
- Do not search for another child skill under this directory.

## Intent: book-calendar-slot

### User request patterns
- book the soonest meeting with
- book the meeting with
- schedule time with a colleague
- find a slot with a teammate
- book a calendar slot with someone

### Retrieval tags
- calendar
- booking
- meeting
- colleague
- schedule

### Answer objective
Book a calendar slot with a colleague, always confirming the chosen employee and the proposed meeting time with the user before the booking is created.

### Instructions
- Extract the colleague name, duration, optional notes, and any date/time phrase the user already provided.
- If the user mentions a date or time phrase, first resolve it by running `python skills/utils/resolve_date_range/scripts/resolve_date_range.py --expression "<required DSL expression>" [--reference-date <optional YYYY-MM-DD>]`.
- Use only tool output for concrete ISO dates.
- Map `startDate -> rangeStart` and `endDate -> rangeEnd` when present.
- Never fabricate dates.
- The booking is a three-step flow. Never skip a confirmation step, even when the search returns a single employee.

**Step 1 — resolve the colleague.** If the user gave a trusted UUID, pass it as `--colleague-id` and go to step 2. If they gave a name, run with `--colleague-name` (duration is not needed for this step): the flow searches employees and returns every match as `candidates` (`nextAction: confirm_colleague_selection`). Show the full candidate list to the user (name, position, department when available) and ask them to confirm which person they mean — even if there is only one candidate. If the user has not given a meeting duration yet, ask for it in the same message. If no employee matches, explain that the colleague could not be found. Never guess which employee to book.

**Candidates come only from tool output.** Present only the employees returned in `candidates` — copy their names and details exactly. If the tool returns an error or no output, tell the user what is missing or ask for the missing detail. Never invent, guess, or embellish employee names, roles, or departments.

**Step 2 — propose a time.** Run with the confirmed `--colleague-id` (no `--confirm`). The flow returns the earliest mutual slot as `selectedSlot` plus the other mutual `slots` (`nextAction: confirm_booking_with_user`). Present the employee and the proposed time to the user and ask whether it is OK. If the user prefers another time, offer the other returned slots.

**Step 3 — book after the user confirms.** Only after the user explicitly agrees to both the employee and the time, re-run with `--colleague-id`, `--slot-start`/`--slot-end` copied **verbatim** from the agreed slot's `start`/`end` strings — including the timezone offset (e.g. `2026-08-21T11:30:00+04:00`) — and `--confirm true`. Never reformat, truncate, or strip the offset. If the slot is no longer available the flow returns `requested_slot_not_available` with fresh slots — go back to step 2 with them.

- Use CLI flags for normal execution; the final JSON-object tail exists only as temporary compatibility.
- `colleagueId`: UUID string (required for steps 2 and 3).
- `colleagueName`: plain string (step 1 only).
- `durationMinutes`: integer; required for steps 2 and 3, optional in step 1.
- `rangeStart` / `rangeEnd`: ISO `YYYY-MM-DD` when present.
- `slotStart` / `slotEnd`: the user-approved slot's `start`/`end` strings copied exactly as returned in the slot output, timezone offset included (step 3).
- `confirm`: pass `true` only in step 3, after the user approved employee and time.
- Omit optional fields if unused.
- `notes`: plain string.

### Execution
```text
# Step 1: resolve colleague by name (returns candidates for the user to choose from)
python skills/calendar/booking/scripts/booking.py --colleague-name "<name>" [--duration-minutes <integer if already known>] [--range-start <optional YYYY-MM-DD>] [--range-end <optional YYYY-MM-DD>]

# Step 2: propose a slot for the confirmed colleague (no booking yet)
python skills/calendar/booking/scripts/booking.py --colleague-id <uuid> --duration-minutes <required integer> [--range-start <optional YYYY-MM-DD>] [--range-end <optional YYYY-MM-DD>]

# Step 3: book the slot the user approved
python skills/calendar/booking/scripts/booking.py --colleague-id <uuid> --duration-minutes <required integer> --slot-start "<start copied verbatim from slots output, offset included>" --slot-end "<end copied verbatim from slots output, offset included>" --confirm true [--range-start <optional YYYY-MM-DD>] [--range-end <optional YYYY-MM-DD>] [--notes "<optional string>"]
```

### Response rule
- Confirm bookings using ISO format `YYYY-MM-DD`.
- Do not include weekday names unless deterministic from tool output.
- Do not mention internal tool names in the user-facing reply.
