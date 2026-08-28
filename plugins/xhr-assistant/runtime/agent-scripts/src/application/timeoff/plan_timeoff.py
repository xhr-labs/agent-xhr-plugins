import json
import re
import unicodedata
from datetime import datetime, timedelta, timezone

from src.core.models.request_context import RequestContext
from src.core.interfaces.http_client import HttpClient
from src.core.models.types import Header
from src.shared.http import FetchJsonError, fetch_json
from src.shared.result import ok_result, error_result

try:
    import icu  # type: ignore
except Exception:
    icu = None

_ICU_TRANSLITERATOR = (
    icu.Transliterator.createInstance("Any-Latin; Latin-ASCII")
    if icu
    else None
)


# =========================
# Helpers
# =========================

def _clean_id(value):
    if isinstance(value, str):
        v = value.strip()
        return v or None
    return None


def _parse_date(value):
    if not value:
        return None
    try:
        v = value.strip() if isinstance(value, str) else value
        if isinstance(v, str) and v.endswith("Z"):
            v = v[:-1] + "+00:00"
        return datetime.fromisoformat(v).date()
    except Exception:
        return None


def _default_window(from_date, to_date):
    today = datetime.now(timezone.utc).date()
    tomorrow = today + timedelta(days=1)

    start = _parse_date(from_date)
    if not start or start < tomorrow:
        start = tomorrow

    end = _parse_date(to_date)
    if not end or end <= start:
        end = start + timedelta(days=180)

    return start, end


def _weekend_from_working_days(working_days):
    day_map = {
        1: "MONDAY",
        2: "TUESDAY",
        3: "WEDNESDAY",
        4: "THURSDAY",
        5: "FRIDAY",
        6: "SATURDAY",
        7: "SUNDAY",
    }

    try:
        working = {int(d) for d in working_days}
    except Exception:
        working = set()

    if not working:
        return {"SATURDAY", "SUNDAY"}

    return {day_map[d] for d in range(1, 8) if d not in working}


DEFAULT_MAX_LEAVE_DAYS = 7
DEFAULT_MAX_TOTAL_DAYS = 16


def _parse_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _parse_number(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0


def _first_field(entry, *keys):
    for key in keys:
        if key in entry:
            return entry.get(key)
    return None


def _is_true(value):
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "y", "on", "enabled"}
    return False


def _get_available_annual_leave(balances):
    for balance in balances:
        time_off_type = _first_field(balance, "time_off_type", "timeOffType") or {}
        if time_off_type.get("name") == "Annual Leave":
            available_balance = _parse_number(_first_field(balance, "available_balance", "availableBalance"))
            advance_leave_limit = (
                _parse_number(_first_field(balance, "advance_leave_limit_days", "advanceLeaveLimitDays"))
                if _is_true(_first_field(balance, "advance_leave_enabled", "advanceLeaveEnabled"))
                else 0
            )
            return int(available_balance + advance_leave_limit)
    return 0


def _approved_leave_dates(approved_leaves):
    dates = set()
    for leave in approved_leaves:
        request_days = leave.get("request_days") or []
        if request_days:
            for day in request_days:
                parsed_date = _parse_date(day.get("request_date"))
                if parsed_date:
                    dates.add(parsed_date)
            continue
        start = _parse_date(leave.get("start_date"))
        end = _parse_date(leave.get("end_date"))
        if start and end:
            current_date = start
            while current_date <= end:
                dates.add(current_date)
                current_date += timedelta(days=1)
        elif start:
            dates.add(start)
    return dates


def _build_blocks(non_working_days):
    blocks = []
    block = []

    for current_date in non_working_days:
        if not block or current_date == block[-1] + timedelta(days=1):
            block.append(current_date)
        else:
            blocks.append(block)
            block = [current_date]
    if block:
        blocks.append(block)

    return [{"start": block[0], "end": block[-1]} for block in blocks]


def _format_date_ranges(date_strings):
    dates = []
    for value in date_strings or []:
        parsed_date = _parse_date(value)
        if parsed_date:
            dates.append(parsed_date)
    if not dates:
        return []
    dates.sort()
    ranges = []
    start = previous = dates[0]
    for current_date in dates[1:]:
        if current_date == previous + timedelta(days=1):
            previous = current_date
            continue
        ranges.append((start, previous))
        start = previous = current_date
    ranges.append((start, previous))
    return [
        f"{start.isoformat()} to {end.isoformat()}" if start != end else start.isoformat()
        for start, end in ranges
    ]


def _format_block_ranges(blocks):
    ranges = []
    for value in blocks or []:
        if isinstance(value, str) and "->" in value:
            start, end = value.split("->", 1)
            ranges.append(f"{start} to {end}")
        elif isinstance(value, str):
            ranges.append(value)
    return ranges


def _holiday_names_in_range(start, end, holiday_map):
    names = []
    current_date = start
    while current_date <= end:
        if current_date in holiday_map:
            for name in sorted(holiday_map[current_date]):
                names.append(f"{name} ({current_date.isoformat()})")
        current_date += timedelta(days=1)
    return names


def _collect_status_ids(statuses):
    status_ids = []
    for status in statuses or []:
        if not isinstance(status, dict):
            continue
        status_id = status.get("id")
        if status_id:
            status_ids.append(status_id)
    return status_ids


def _holiday_blocks_for_patterns(blocks, holiday_map, patterns):
    matches = []
    if not patterns:
        return matches
    for block in blocks:
        names = set()
        current_date = block["start"]
        while current_date <= block["end"]:
            names_for_date = holiday_map.get(current_date) or []
            for name in names_for_date:
                if _holiday_matches([name], patterns):
                    names.add(name)
            current_date += timedelta(days=1)
        if names:
            matches.append({
                "start": block["start"],
                "end": block["end"],
                "names": sorted(names),
            })
    return matches


def _task_busy_dates(tasks):
    dates = set()
    tasks_with_dates = []
    for task in tasks or []:
        if not isinstance(task, dict):
            continue
        start = _parse_date(task.get("start_date"))
        end = _parse_date(task.get("due_date"))
        if not start or not end:
            continue
        if end < start:
            start, end = end, start
        current_date = start
        while current_date <= end:
            dates.add(current_date)
            current_date += timedelta(days=1)
        tasks_with_dates.append({
            "id": task.get("id"),
            "name": task.get("name"),
            "start_date": start.isoformat(),
            "due_date": end.isoformat(),
        })
    return dates, tasks_with_dates


def _same_block(left, right):
    return left["start"] == right["start"] and left["end"] == right["end"]


def _blocks_for_range(non_working_blocks, start, end):
    return [
        f"{block['start'].isoformat()}->{block['end'].isoformat()}"
        for block in non_working_blocks
        if block["end"] >= start and block["start"] <= end
    ]


def _build_extension_plan(
    block,
    target_total_days,
    direction,
    non_working_set,
    approved_leave_dates,
    task_busy_dates,
    available_leave,
    max_leave_days,
    window_start,
    window_end,
    allow_overdraft,
):
    start = block["start"]
    end = block["end"]
    total_days = (end - start).days + 1
    if total_days > target_total_days:
        return None

    leave_dates = []
    leave_required = 0
    if direction == "before":
        current_date = start - timedelta(days=1)
        while total_days < target_total_days and current_date >= window_start:
            if current_date in task_busy_dates:
                return None
            if current_date not in non_working_set and current_date not in approved_leave_dates:
                leave_dates.append(current_date)
                leave_required += 1
            total_days += 1
            start = current_date
            current_date -= timedelta(days=1)
    else:
        current_date = end + timedelta(days=1)
        while total_days < target_total_days and current_date <= window_end:
            if current_date in task_busy_dates:
                return None
            if current_date not in non_working_set and current_date not in approved_leave_dates:
                leave_dates.append(current_date)
                leave_required += 1
            total_days += 1
            end = current_date
            current_date += timedelta(days=1)

    if total_days < target_total_days:
        return None
    if max_leave_days is not None and leave_required > max_leave_days:
        return None
    if not allow_overdraft and leave_required > available_leave:
        return None

    leave_dates = sorted(leave_dates)
    return {
        "start": start,
        "end": end,
        "totalDays": total_days,
        "leaveDaysRequired": leave_required,
        "leaveDates": leave_dates,
    }


def _normalize_text(value):
    if value is None:
        return ""
    text = str(value)
    if _ICU_TRANSLITERATOR:
        text = _ICU_TRANSLITERATOR.transliterate(text)
    else:
        text = unicodedata.normalize("NFKD", text)
        text = "".join(
            character for character in text
            if unicodedata.category(character) not in {"Mn", "Me", "Cf"}
        )
    cleaned = []
    for character in text:
        category = unicodedata.category(character)
        if category and category[0] in {"L", "N"}:
            cleaned.append(character)
        else:
            cleaned.append(" ")
    text = re.sub(r"\s+", " ", "".join(cleaned)).strip()
    return text.casefold()


def _holiday_patterns(filter_text):
    if filter_text is None:
        return []
    if isinstance(filter_text, (list, tuple, set)):
        parts = []
        for item in filter_text:
            parts.extend(_holiday_patterns(item))
        return sorted(set(pattern for pattern in parts if pattern))
    text = str(filter_text)
    raw_parts = re.split(r"[;,|]+", text)
    patterns = []
    for part in raw_parts:
        normalized = _normalize_text(part)
        if normalized:
            patterns.append(normalized)
    return sorted(set(patterns))


def _holiday_matches(holiday_names, patterns):
    if not patterns:
        return True
    stopwords = {"day", "days", "holiday", "holidays", "festival"}
    for name in holiday_names or []:
        normalized_name = _normalize_text(name)
        name_tokens = {token for token in normalized_name.split() if token and token not in stopwords}
        for pattern in patterns:
            if pattern and pattern in normalized_name:
                return True
            pattern_tokens = {token for token in pattern.split() if token and token not in stopwords}
            if pattern_tokens and name_tokens and pattern_tokens.intersection(name_tokens):
                return True
    return False


# =========================
# Main
# =========================

async def run(task_args, context: RequestContext, http_client: HttpClient):
    api_base_url = context.api_base_url
    headers_in = context.request_headers
    headers = context.headers

    args = task_args if isinstance(task_args, dict) else {}
    employee_id = _clean_id(headers_in.get(Header.X_EMPLOYEE_ID))

    if not employee_id:
        return {"ok": False, "error": "missing_employee_id"}

    requested_year = _parse_int(args.get("year"))
    from_date = args.get("from_date") or args.get("fromDate")
    to_date = args.get("to_date") or args.get("toDate")
    if requested_year is not None:
        from_date = from_date or f"{requested_year:04d}-01-01"
        to_date = to_date or f"{requested_year:04d}-12-31"

    window_start, window_end = _default_window(
        from_date,
        to_date,
    )
    year = requested_year or window_start.year
    max_leave_days = _parse_int(args.get("max_leave_days") or args.get("maxLeaveDays"))
    max_total_days_arg = _parse_int(
        args.get("max_total_days") or args.get("maxTotalDays") or args.get("total_days") or args.get("totalDays")
    )
    holiday_filter = args.get("holiday_name") or args.get("holidayName") or args.get("holiday")
    if max_leave_days is not None and max_leave_days < 0:
        max_leave_days = None
    if max_total_days_arg is not None and max_total_days_arg < 0:
        max_total_days_arg = None
    holiday_patterns = _holiday_patterns(holiday_filter)
    allow_overdraft = bool(holiday_patterns and max_total_days_arg is not None)

    try:
        async with http_client.session() as client:
            emp_payload = await fetch_json(
                client,
                f"{api_base_url}/v1/em/employees/{employee_id}",
                headers=headers,
            )
            employee = emp_payload.get("data") or {}
            location = employee.get("work_location") or {}
            location_id = location.get("id")
            weekend_days = _weekend_from_working_days(location.get("working_days") or [])

            holidays = []
            if location_id:
                for current_year in range(window_start.year, window_end.year + 1):
                    try:
                        payload = await fetch_json(
                            client,
                            f"{api_base_url}/v1/cm/locations/{location_id}/holidays",
                            headers=headers,
                            params={"year": current_year},
                        )
                    except FetchJsonError as exc:
                        # A location may have calendars configured for only some
                        # years in a planning window. Treat a missing calendar as
                        # no holidays for that year, while preserving all other
                        # backend failures.
                        if exc.status_code == 404:
                            continue
                        raise
                    holidays.extend(payload.get("data") or [])

            leaves_payload = await fetch_json(
                client,
                f"{api_base_url}/v1/to/time-off-requests",
                headers=headers,
                params={
                    "employeeId.equals": employee_id,
                    "status.equals": "APPROVED",
                    "startDate.lessThanOrEqual": f"{window_end}T23:59:59Z",
                    "endDate.greaterThanOrEqual": f"{window_start}T00:00:00Z",
                },
            )
            approved_leaves = leaves_payload.get("data") or []

            balances_payload = await fetch_json(
                client,
                f"{api_base_url}/v1/to/time-off-balances",
                headers=headers,
                params={
                    "employeeId.equals": employee_id,
                    "year.equals": year,
                },
            )
            balances = [balance for balance in (balances_payload.get("data") or []) if balance.get("active") is True]

            statuses_payload = await fetch_json(
                client,
                f"{api_base_url}/v1/pm/statuses",
                headers=headers,
            )
            statuses_data = statuses_payload.get("data") if isinstance(statuses_payload, dict) else []
            status_ids = _collect_status_ids(statuses_data)

            tasks = []
            if status_ids:
                tasks_payload = await fetch_json(
                    client,
                    f"{api_base_url}/v1/pm/tasks/basic-info",
                    method="POST",
                    headers=headers,
                    json={
                        "status_ids": status_ids,
                        "page_size": 200,
                        "page_number": 0,
                        "assignee_ids": [employee_id],
                    },
                )
                tasks = tasks_payload.get("data") if isinstance(tasks_payload, dict) else []
    except FetchJsonError as exc:
        return error_result(f"{exc.as_error()} {str(exc.status_code or 500)}",)

    holiday_dates = {
        _parse_date(holiday.get("date"))
        for holiday in holidays
        if _parse_date(holiday.get("date"))
    }
    holiday_map = {}
    for holiday in holidays:
        parsed_date = _parse_date(holiday.get("date"))
        name = holiday.get("name")
        if parsed_date and name:
            holiday_map.setdefault(parsed_date, set()).add(name)
    approved_leave_dates = _approved_leave_dates(approved_leaves)
    task_busy_dates, tasks_with_dates = _task_busy_dates(tasks)
    available_leave = _get_available_annual_leave(balances)
    if max_total_days_arg is not None:
        max_total_days = max_total_days_arg
        if max_leave_days is None:
            if allow_overdraft:
                max_leave_days = None
            else:
                max_leave_days = min(available_leave, max_total_days)
    else:
        if max_leave_days is None:
            max_leave_days = min(available_leave, DEFAULT_MAX_LEAVE_DAYS)
            max_total_days = DEFAULT_MAX_TOTAL_DAYS
        else:
            max_total_days = max_leave_days + 8

    non_working_days = []
    current_date = window_start - timedelta(days=7)
    window_end_with_padding = window_end + timedelta(days=7)

    while current_date <= window_end_with_padding:
        if current_date in holiday_dates or current_date.strftime("%A").upper() in weekend_days:
            non_working_days.append(current_date)
        current_date += timedelta(days=1)

    non_working_days = sorted(set(non_working_days) - task_busy_dates)

    non_working_blocks = _build_blocks(non_working_days)
    holiday_blocks = _holiday_blocks_for_patterns(non_working_blocks, holiday_map, holiday_patterns)
    primary_holiday_block = holiday_blocks[0] if holiday_blocks else None
    candidate_blocks = [
        block for block in non_working_blocks
        if block["end"] >= window_start and block["start"] <= window_end
    ]

    candidate_plans = []
    for start_index in range(len(candidate_blocks)):
        leave_dates = []
        leave_required = 0
        for end_index in range(start_index, len(candidate_blocks)):
            if end_index > start_index:
                gap_start = candidate_blocks[end_index - 1]["end"] + timedelta(days=1)
                gap_end = candidate_blocks[end_index]["start"]

                current_date = gap_start
                invalid_plan = False
                while current_date < gap_end:
                    if current_date in task_busy_dates:
                        invalid_plan = True
                        break
                    if current_date not in approved_leave_dates:
                        leave_dates.append(current_date)
                        leave_required += 1
                    current_date += timedelta(days=1)

                if invalid_plan:
                    break

            if leave_required > available_leave:
                break
            if max_leave_days is not None and leave_required > max_leave_days:
                break

            start = candidate_blocks[start_index]["start"]
            end = candidate_blocks[end_index]["end"]
            total_days = (end - start).days + 1
            if total_days > max_total_days:
                break
            blocks_used = [
                f"{block['start'].isoformat()}->{block['end'].isoformat()}"
                for block in candidate_blocks[start_index : end_index + 1]
            ]
            leave_dates_iso = [date.isoformat() for date in leave_dates]
            holiday_names = _holiday_names_in_range(start, end, holiday_map)
            candidate_plans.append({
                "start": start.isoformat(),
                "end": end.isoformat(),
                "totalDays": total_days,
                "leaveDaysRequired": leave_required,
                "leaveDates": leave_dates_iso,
                "leaveDateRanges": _format_date_ranges(leave_dates_iso),
                "blocksUsed": blocks_used,
                "blocksUsedRanges": _format_block_ranges(blocks_used),
                "holidayNames": holiday_names,
                "timeOffType": "Annual Leave",
                "remainingLeaveBalance": max(available_leave - leave_required, 0),
            })

    candidate_plans.sort(key=lambda plan: (-plan["totalDays"], plan["leaveDaysRequired"], plan["start"]))
    if holiday_patterns:
        candidate_plans = [
            plan for plan in candidate_plans
            if _holiday_matches(plan.get("holidayNames"), holiday_patterns)
        ]
    if max_total_days_arg is not None:
        exact_plans = [plan for plan in candidate_plans if plan["totalDays"] == max_total_days_arg]
        if exact_plans:
            candidate_plans = exact_plans
        else:
            candidate_plans = []
            if holiday_patterns and primary_holiday_block:
                non_working_set = set(non_working_days)
                before_plan = _build_extension_plan(
                    primary_holiday_block,
                    max_total_days_arg,
                    "before",
                    non_working_set,
                    approved_leave_dates,
                    task_busy_dates,
                    available_leave,
                    max_leave_days,
                    window_start,
                    window_end,
                    allow_overdraft,
                )
                after_plan = _build_extension_plan(
                    primary_holiday_block,
                    max_total_days_arg,
                    "after",
                    non_working_set,
                    approved_leave_dates,
                    task_busy_dates,
                    available_leave,
                    max_leave_days,
                    window_start,
                    window_end,
                    allow_overdraft,
                )
                for plan in (before_plan, after_plan):
                    if not plan:
                        continue
                    blocks_used = _blocks_for_range(non_working_blocks, plan["start"], plan["end"])
                    leave_dates_iso = [date.isoformat() for date in plan["leaveDates"]]
                    holiday_names = _holiday_names_in_range(plan["start"], plan["end"], holiday_map)
                    candidate_plans.append({
                        "start": plan["start"].isoformat(),
                        "end": plan["end"].isoformat(),
                        "totalDays": plan["totalDays"],
                        "leaveDaysRequired": plan["leaveDaysRequired"],
                        "leaveDates": leave_dates_iso,
                        "leaveDateRanges": _format_date_ranges(leave_dates_iso),
                        "blocksUsed": blocks_used,
                        "blocksUsedRanges": _format_block_ranges(blocks_used),
                        "holidayNames": holiday_names,
                        "timeOffType": "Annual Leave",
                        "remainingLeaveBalance": available_leave - plan["leaveDaysRequired"],
                    })
    max_plans = 30
    if len(candidate_plans) > max_plans:
        candidate_plans = candidate_plans[:max_plans]

    next_blocks = [block for block in non_working_blocks if block["end"] >= window_start]
    if primary_holiday_block:
        next_blocks = [
            primary_holiday_block,
            *[block for block in next_blocks if not _same_block(block, primary_holiday_block)],
        ]
    next_block_ranges = [
        f"{block['start'].isoformat()} to {block['end'].isoformat()}"
        for block in next_blocks[:3]
    ]

    payload = {
        "ok": True,
        "data": {
            "timeWindow": {"from": window_start.isoformat(), "to": window_end.isoformat()},
            "employee": {
                "id": employee_id,
                "workLocationId": location_id,
                "weekendDays": sorted(weekend_days),
            },
            "totalDaysRequested": max_total_days_arg,
            "holidayNameRequested": holiday_filter,
            "publicHolidays": holidays,
            "approvedLeaveRequests": approved_leaves,
            "leaveBalances": balances,
            "tasksWithDateRanges": tasks_with_dates,
            "taskBlockedDates": [date.isoformat() for date in sorted(task_busy_dates)],
            "nonWorkingDays": [date.isoformat() for date in non_working_days],
        },
        "meta": {
            "employeeId": employee_id,
            "year": year,
            "source": "timeoff_plan",
        },
    }
    if candidate_plans:
        payload["data"].pop("summary", None)
        recommended_plans = candidate_plans[:3]
        payload["data"]["candidatePlans"] = candidate_plans
        payload["data"]["recommendedPlans"] = recommended_plans
    else:
        payload["data"].pop("candidatePlans", None)
        payload["data"].pop("recommendedPlans", None)
        next_step = "Provide a narrower date range or max_leave_days/max_total_days to generate options."
        if max_total_days_arg is not None:
            next_step = f"No plans match totalDays={max_total_days_arg}. Try a different totalDays or date range."
        if holiday_patterns and not candidate_plans:
            if primary_holiday_block:
                block_len = (primary_holiday_block["end"] - primary_holiday_block["start"]).days + 1
                extra_days = max_total_days_arg - block_len
                holiday_names = ", ".join(primary_holiday_block["names"])
                block_range = f"{primary_holiday_block['start'].isoformat()} to {primary_holiday_block['end'].isoformat()}"
                if extra_days > 0:
                    next_step = (
                        f"Holiday block {holiday_names} is {block_range} ({block_len} days). "
                        f"To reach totalDays={max_total_days_arg}, add {extra_days} leave days before or after this block."
                    )
                else:
                    next_step = f"Holiday block {holiday_names} is {block_range}. Try extending before or after this block."
            else:
                next_step = "No plans match the requested holiday. Try a different holiday name or date range."
        summary = {
            "timeWindow": {"from": window_start.isoformat(), "to": window_end.isoformat()},
            "availableAnnualLeave": available_leave,
            "nextNonWorkingBlocks": next_block_ranges,
            "nextStepNeeded": next_step,
        }
        payload["data"]["summary"] = summary

    return payload
