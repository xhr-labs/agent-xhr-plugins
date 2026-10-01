from datetime import datetime, timezone, date, timedelta
import calendar
import re
from src.shared.result import ok_result, error_result


RELATIVE_WEEKDAY_RE = [
    re.compile(
        r"^(next|last|this)\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)$",
        re.IGNORECASE,
    ),
    re.compile(
        r"^(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\s+(?:of\s+)?(next|last|this)\s+week$",
        re.IGNORECASE,
    ),
    re.compile(
        r"^(next|last|this)\s+week\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)$",
        re.IGNORECASE,
    ),
]
WEEK_OF_RE = re.compile(r"week of (.+)", re.IGNORECASE)
NTH_WEEK_OF_MONTH_RE = re.compile(r"(\w+|\d+(?:st|nd|rd|th)) week of ([a-zA-Z]+)(?: (\d{4}))?", re.IGNORECASE)
NTH_WEEKDAY_OF_MONTH_RE = re.compile(
    r"(\w+|\d+(?:st|nd|rd|th))\s+"
    r"(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\s+of\s+"
    r"([a-zA-Z]+)\s+(\d{4})$",
    re.IGNORECASE,
)
ORDINAL_RE = re.compile(r"(\d+)(st|nd|rd|th)")
RELATIVE_DAY_RANGE_RE = re.compile(
    r"^(next|upcoming|last|past|previous)\s+(\d+)\s+days?$",
    re.IGNORECASE,
)

WEEKDAY_MAP = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6,
}

WEEKDAY_START = 0  # 0 = Monday, 6 = Sunday

HOLIDAY_MAP = {
    "christmas": {"month": 12, "day": 25},
    "new year": {"month": 1, "day": 1},
    "new years day": {"month": 1, "day": 1},
    "valentines day": {"month": 2, "day": 14},
    "halloween": {"month": 10, "day": 31},
    "independence day (us)": {"month": 7, "day": 4},
    "labor day (us)": {"month": 9, "weekday": 0, "nth": 1},
    "thanksgiving (us)": {"month": 11, "weekday": 3, "nth": 4},
    "easter": None,
    "eid al-fitr": None,
    "eid al-adha": None,
    "lunar new year": None,
}


def normalize_holiday_expression(expr: str, target_year: int):
    expr = expr.lower()
    for holiday, info in HOLIDAY_MAP.items():
        if holiday in expr:
            if info is None:
                return None
            month = info.get("month")
            day = info.get("day")
            weekday = info.get("weekday")
            nth = info.get("nth")

            if month and day:
                if re.search(r"\bweek\b", expr):
                    return f"week of {calendar.month_name[month]} {day}, {target_year}"
                return f"{calendar.month_name[month]} {day}, {target_year}"

            if month and weekday is not None and nth is not None:
                c = calendar.Calendar()
                month_days = [
                    d for d in c.itermonthdates(target_year, month)
                    if d.month == month and d.weekday() == weekday
                ]
                if not month_days or nth > len(month_days):
                    return None
                target = month_days[nth - 1]
                if re.search(r"\bweek\b", expr):
                    return f"week of {target.strftime('%B %d, %Y')}"
                return target.strftime("%B %d, %Y")
    return None


def _get_week_of_month(year: int, month: int, week_index: int):
    first_day = date(year, month, 1)
    first_week_start = first_day - timedelta(days=(first_day.weekday() - WEEKDAY_START) % 7)
    start = first_week_start + timedelta(weeks=week_index - 1)
    end = start + timedelta(days=6)

    if start.month < month:
        start = date(year, month, 1)
    last_day = date(year, month, calendar.monthrange(year, month)[1])
    if end.month > month:
        end = last_day

    return {"startDate": start.isoformat(), "endDate": end.isoformat()}


def _get_last_week_of_month(year: int, month: int):
    last_day = date(year, month, calendar.monthrange(year, month)[1])
    start = last_day - timedelta(days=(last_day.weekday() - WEEKDAY_START) % 7)
    return {"startDate": start.isoformat(), "endDate": last_day.isoformat()}


def _get_nth_weekday_of_month(year: int, month: int, weekday: int, nth: str):
    c = calendar.Calendar()
    month_days = [
        d for d in c.itermonthdates(year, month)
        if d.month == month and d.weekday() == weekday
    ]
    if not month_days:
        return None
    if nth == "last":
        target = month_days[-1]
    else:
        nth_map = {"first": 1, "second": 2, "third": 3, "fourth": 4, "fifth": 5}
        week_index = nth_map.get(nth)
        if not week_index or week_index > len(month_days):
            return None
        target = month_days[week_index - 1]
    return {"startDate": target.isoformat(), "endDate": target.isoformat()}


def _normalize_nth(nth: str) -> str:
    nth = nth.lower()
    valid_words = {"first", "second", "third", "fourth", "fifth", "last"}
    if nth in valid_words:
        return nth
    match = ORDINAL_RE.match(nth)
    if match:
        num = int(match.group(1))
        mapping = {1: "first", 2: "second", 3: "third", 4: "fourth", 5: "fifth"}
        return mapping.get(num, nth)
    return nth


def _parse_month_name(raw: str):
    raw_lower = raw.lower()
    for i, name in enumerate(calendar.month_name):
        if i == 0:
            continue
        if raw_lower == name.lower():
            return i
    for i, abbr in enumerate(calendar.month_abbr):
        if i == 0:
            continue
        if raw_lower == abbr.lower():
            return i
    return None


def _parse_date_flexible(raw: str, default_year: int):
    formats_with_year = [
        "%B %d, %Y",
        "%b %d, %Y",
        "%B %d %Y",
        "%b %d %Y",
        "%d %B %Y",
    ]
    formats_without_year = ["%B %d", "%b %d", "%d %B"]

    for fmt in formats_with_year:
        try:
            return datetime.strptime(raw, fmt).date()
        except ValueError:
            continue

    for fmt in formats_without_year:
        try:
            return datetime.strptime(f"{default_year} {raw}", f"%Y {fmt}").date()
        except ValueError:
            continue

    return None


def _get_month_range(year: int, month: int):
    start = date(year, month, 1)
    last_day = calendar.monthrange(year, month)[1]
    end = date(year, month, last_day)
    return {"startDate": start.isoformat(), "endDate": end.isoformat()}


def resolve_date_range(expression: str, reference_date: str = None, use_reference_year_for_relative: bool = False):
    try:
        ref_date = date.fromisoformat(reference_date) if reference_date else datetime.now(timezone.utc).date()
        today = datetime.now(timezone.utc).date()

        anchor_date = ref_date if use_reference_year_for_relative else today
        target_year = anchor_date.year
        expr = expression.strip()
        expr_lower = expr.lower()

        if "next year" in expr_lower:
            target_year += 1
        elif "last year" in expr_lower:
            target_year -= 1

        if expr_lower == "today":
            return {"startDate": anchor_date.isoformat(), "endDate": anchor_date.isoformat()}
        if expr_lower == "tomorrow":
            day = anchor_date + timedelta(days=1)
            return {"startDate": day.isoformat(), "endDate": day.isoformat()}
        if expr_lower == "yesterday":
            day = anchor_date - timedelta(days=1)
            return {"startDate": day.isoformat(), "endDate": day.isoformat()}

        if expr_lower in {"this year", "current year", "next year", "last year"}:
            year = target_year
            start = date(year, 1, 1)
            end = date(year, 12, 31)
            return {"startDate": start.isoformat(), "endDate": end.isoformat()}

        match = RELATIVE_DAY_RANGE_RE.match(expr_lower)
        if match:
            direction, days_str = match.groups()
            days = int(days_str)
            if days <= 0:
                return {"error": f"Unsupported expression: {expression}"}

            direction = direction.lower()
            if direction in {"next", "upcoming"}:
                start = anchor_date
                end = anchor_date + timedelta(days=days - 1)
            else:
                start = anchor_date - timedelta(days=days - 1)
                end = anchor_date

            return {"startDate": start.isoformat(), "endDate": end.isoformat()}

        current_wd = anchor_date.weekday()
        start_of_week = anchor_date - timedelta(days=(current_wd - WEEKDAY_START) % 7)
        if expr_lower in {"this week", "current week"}:
            start = start_of_week
            return {"startDate": start.isoformat(), "endDate": (start + timedelta(days=6)).isoformat()}
        if expr_lower == "next week":
            start = start_of_week + timedelta(weeks=1)
            return {"startDate": start.isoformat(), "endDate": (start + timedelta(days=6)).isoformat()}
        if expr_lower == "last week":
            start = start_of_week - timedelta(weeks=1)
            return {"startDate": start.isoformat(), "endDate": (start + timedelta(days=6)).isoformat()}

        if expr_lower == "this month":
            return _get_month_range(anchor_date.year, anchor_date.month)
        if expr_lower == "next month":
            year = anchor_date.year + (1 if anchor_date.month == 12 else 0)
            month = 1 if anchor_date.month == 12 else anchor_date.month + 1
            return _get_month_range(year, month)
        if expr_lower == "last month":
            year = anchor_date.year - (1 if anchor_date.month == 1 else 0)
            month = 12 if anchor_date.month == 1 else anchor_date.month - 1
            return _get_month_range(year, month)

        if "next month" in expr_lower:
            next_month = 1 if anchor_date.month == 12 else anchor_date.month + 1
            next_year = anchor_date.year + (1 if anchor_date.month == 12 else 0)
            expr = re.sub(r"next month", f"{calendar.month_name[next_month]} {next_year}", expr, flags=re.IGNORECASE)
            expr_lower = expr.lower()
        elif "last month" in expr_lower:
            last_month = 12 if anchor_date.month == 1 else anchor_date.month - 1
            last_year = anchor_date.year - (1 if anchor_date.month == 1 else 0)
            expr = re.sub(r"last month", f"{calendar.month_name[last_month]} {last_year}", expr, flags=re.IGNORECASE)
            expr_lower = expr.lower()
        elif "this month" in expr_lower:
            expr = re.sub(r"this month", f"{calendar.month_name[anchor_date.month]} {anchor_date.year}", expr, flags=re.IGNORECASE)
            expr_lower = expr.lower()

        match_a, match_b, match_c = (pattern.match(expr_lower) for pattern in RELATIVE_WEEKDAY_RE)

        if match_a:
            rel, weekday_name = match_a.groups()
        elif match_b:
            weekday_name, rel = match_b.groups()
        elif match_c:
            rel, weekday_name = match_c.groups()
        else:
            rel = weekday_name = None

        if weekday_name:
            weekday_num = WEEKDAY_MAP[weekday_name]

            if rel == "this":
                target = start_of_week + timedelta(days=weekday_num)
            elif rel == "next":
                if match_a:
                    delta = (weekday_num - current_wd + 7) % 7 or 7
                    target = anchor_date + timedelta(days=delta)
                else:
                    start_of_next_week = start_of_week + timedelta(weeks=1)
                    target = start_of_next_week + timedelta(days=weekday_num)
            else:
                start_of_last_week = start_of_week - timedelta(weeks=1)
                target = start_of_last_week + timedelta(days=weekday_num)

            return {"startDate": target.isoformat(), "endDate": target.isoformat()}

        if expr_lower in WEEKDAY_MAP:
            base_for_weekday = ref_date or anchor_date
            weekday_num = WEEKDAY_MAP[expr_lower]
            base_weekday = base_for_weekday.weekday()
            delta = (weekday_num - base_weekday) % 7
            target = base_for_weekday + timedelta(days=delta or 7)
            return {"startDate": target.isoformat(), "endDate": target.isoformat()}

        normalized = normalize_holiday_expression(expr, target_year)
        if normalized:
            expr = normalized
            expr_lower = expr.lower()

        match = WEEK_OF_RE.match(expr_lower)
        if match:
            raw_date_expr = match.group(1).strip()
            rel_match = re.match(r"(next|last|this)\s+(\w+)", raw_date_expr)
            if rel_match:
                rel, weekday_name = rel_match.groups()
                weekday_num = WEEKDAY_MAP.get(weekday_name)
                if weekday_num is not None:
                    if rel == "this":
                        delta = (weekday_num - current_wd) % 7
                        dt = anchor_date + timedelta(days=delta)
                    elif rel == "next":
                        delta = (weekday_num - current_wd + 7) % 7 or 7
                        dt = anchor_date + timedelta(days=delta)
                    else:
                        delta = (weekday_num - current_wd - 7) % 7 or -7
                        dt = anchor_date + timedelta(days=delta)
                else:
                    dt = None
            else:
                dt = _parse_date_flexible(raw_date_expr, target_year)

            if not dt:
                return {"error": f"Invalid date in expression: {raw_date_expr}"}
            start = dt - timedelta(days=(dt.weekday() - WEEKDAY_START) % 7)
            end = start + timedelta(days=6)
            return {"startDate": start.isoformat(), "endDate": end.isoformat()}

        match = NTH_WEEK_OF_MONTH_RE.match(expr.strip())
        if match:
            nth_raw, month_name, year_str = match.groups()
            nth = _normalize_nth(nth_raw)
            month = None
            for i, m in enumerate(calendar.month_name):
                if m.lower() == month_name.lower():
                    month = i
                    break
            if not month:
                return {"error": f"Unsupported month: {month_name}"}
            year = int(year_str) if year_str else target_year
            if nth == "last":
                return _get_last_week_of_month(year, month)
            nth_map = {"first": 1, "second": 2, "third": 3, "fourth": 4, "fifth": 5}
            week_index = nth_map.get(nth)
            if not week_index:
                return {"error": f"Unsupported nth value: {nth_raw}"}
            return _get_week_of_month(year, month, week_index)

        match = NTH_WEEKDAY_OF_MONTH_RE.match(expr.strip())
        if match:
            nth_raw, weekday_name, month_name, year_str = match.groups()
            nth = _normalize_nth(nth_raw)
            month = _parse_month_name(month_name)
            if not month:
                return {"error": f"Unsupported month: {month_name}"}
            weekday_num = WEEKDAY_MAP.get(weekday_name.lower())
            if weekday_num is None:
                return {"error": f"Unsupported weekday: {weekday_name}"}
            target = _get_nth_weekday_of_month(int(year_str), month, weekday_num, nth)
            if not target:
                return {"error": f"Unsupported nth value: {nth_raw}"}
            return target

        month_year_match = re.match(r"^([a-zA-Z]+)\s+(\d{4})$", expr.strip())
        if month_year_match:
            month_name, year_str = month_year_match.groups()
            month = _parse_month_name(month_name)
            if month:
                return _get_month_range(int(year_str), month)
            return {"error": f"Unsupported month: {month_name}"}

        month_only_match = re.match(r"^([a-zA-Z]+)$", expr.strip())
        if month_only_match:
            month_name = month_only_match.group(1)
            month = _parse_month_name(month_name)
            if month:
                return _get_month_range(target_year, month)
            return {"error": f"Unsupported month: {month_name}"}

        dt = _parse_date_flexible(expr, target_year)
        if dt:
            return {"startDate": dt.isoformat(), "endDate": dt.isoformat()}

        return {"error": f"Unsupported expression: {expression}"}
    except Exception as exc:
        return {"error": f"Error processing expression '{expression}': {str(exc)}"}


async def run(task_args, context=None, http_client=None):
    task_args = task_args if isinstance(task_args, dict) else {}
    expression = task_args.get("expression")
    reference_date = task_args.get("referenceDate")
    use_reference_year_for_relative = bool(task_args.get("useReferenceYearForRelative", False))

    if not expression or not isinstance(expression, str):
        payload = {"error": "Missing expression"}
    else:
        payload = resolve_date_range(
            expression=expression,
            reference_date=reference_date,
            use_reference_year_for_relative=use_reference_year_for_relative,
        )

    if isinstance(payload, dict) and payload.get("error"):
        return error_result(str(payload.get("error")),)

    return ok_result({
        "data": payload,
        "meta": None,
        "query": {
            "expression": expression,
            "referenceDate": reference_date,
            "useReferenceYearForRelative": use_reference_year_for_relative,
        },
    })
