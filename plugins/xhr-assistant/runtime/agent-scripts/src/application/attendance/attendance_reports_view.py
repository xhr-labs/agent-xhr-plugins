from __future__ import annotations

from typing import Any

from src.application.attendance.attendance_reports_common import (
    format_duration,
    format_signed_minutes,
    get_regular_overtime_balance_minutes,
    get_report_overtime_display_minutes,
    to_total_minutes,
)


def format_period_report_rows(
    reports: list[dict[str, Any]], status: str
) -> list[dict[str, Any]]:
    formatted = []
    for item in reports:
        employee = item.get("employee") or {}
        approved_hours_dict = item.get("approvedHours")
        rest_day_ot = item.get("restDayOvertimeHours")
        holiday_ot = item.get("publicHolidayOvertimeHours")
        night_ot = item.get("nightOvertimeHours")
        target_hours_dict = item.get("targetHours")

        overtime_display_mins = get_report_overtime_display_minutes(item, status)
        regular_ot_balance_mins = get_regular_overtime_balance_minutes(
            overtime_display_mins, rest_day_ot, holiday_ot
        )

        row: dict[str, Any] = {
            "employee": {
                "id": employee.get("id"),
                "name": employee.get("name"),
                "businessId": employee.get("businessId"),
                "title": employee.get("title") or employee.get("position"),
                "avatarUrl": employee.get("avatarUrl"),
                "departments": employee.get("departments") or [],
                "employmentType": employee.get("employmentType"),
            },
            "status": status,
            "targetHours": format_duration(target_hours_dict),
            "targetMinutes": to_total_minutes(target_hours_dict),
            "overtimeHours": format_signed_minutes(overtime_display_mins),
            "overtimeMinutes": overtime_display_mins,
            "regularOvertimeHours": format_signed_minutes(regular_ot_balance_mins),
            "regularOvertimeMinutes": regular_ot_balance_mins,
            "restDayOvertimeHours": format_signed_minutes(to_total_minutes(rest_day_ot)),
            "restDayOvertimeMinutes": to_total_minutes(rest_day_ot),
            "publicHolidayOvertimeHours": format_signed_minutes(to_total_minutes(holiday_ot)),
            "publicHolidayOvertimeMinutes": to_total_minutes(holiday_ot),
            "nightOvertimeHours": format_duration(night_ot),
            "nightOvertimeMinutes": to_total_minutes(night_ot),
            "departments": employee.get("departments") or [],
            "employmentType": employee.get("employmentType"),
        }

        if status == "PENDING":
            row["hoursAwaitingApproval"] = format_duration(approved_hours_dict)
            row["hoursAwaitingApprovalMinutes"] = to_total_minutes(approved_hours_dict)
        else:
            row["approvedHours"] = format_duration(approved_hours_dict)
            row["approvedMinutes"] = to_total_minutes(approved_hours_dict)

        formatted.append(row)
    return formatted


def format_annual_report_rows(
    reports: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    formatted = []
    for item in reports:
        employee = item.get("employee") or {}
        balance_minutes = item.get("balanceMinutes", 0)
        rest_day_ot = item.get("restDayOvertimeHours")
        holiday_ot = item.get("publicHolidayOvertimeHours")
        night_ot = item.get("nightOvertimeHours")
        regular_ot_balance_mins = get_regular_overtime_balance_minutes(
            balance_minutes, rest_day_ot, holiday_ot
        )

        monthly_buckets = []
        for bucket in item.get("monthly") or []:
            month_num = bucket.get("month")
            month_balance = bucket.get("balanceMinutes", 0)
            month_running = bucket.get("runningBalanceMinutes", 0)
            monthly_buckets.append({
                "month": month_num,
                "balanceMinutes": month_balance,
                "balanceHours": format_signed_minutes(month_balance),
                "runningBalanceMinutes": month_running,
                "runningBalanceHours": format_signed_minutes(month_running),
                "paidHours": format_duration(bucket.get("paidHours")),
                "actualWorkedHours": format_duration(bucket.get("actualWorkedHours")),
                "targetHours": format_duration(bucket.get("targetHours")),
            })

        formatted.append({
            "employee": {
                "id": employee.get("id"),
                "name": employee.get("name"),
                "businessId": employee.get("businessId"),
                "title": employee.get("title"),
                "avatarUrl": employee.get("avatarUrl"),
                "departments": employee.get("departments") or [],
                "employmentType": employee.get("employmentType"),
            },
            "year": item.get("year"),
            "paidHours": format_duration(item.get("paidHours")),
            "paidMinutes": to_total_minutes(item.get("paidHours")),
            "actualWorkedHours": format_duration(item.get("actualWorkedHours")),
            "actualWorkedMinutes": to_total_minutes(item.get("actualWorkedHours")),
            "publicHolidayHours": format_duration(item.get("publicHolidayHours")),
            "publicHolidayMinutes": to_total_minutes(item.get("publicHolidayHours")),
            "vacationHours": format_duration(item.get("vacationHours")),
            "vacationMinutes": to_total_minutes(item.get("vacationHours")),
            "targetHours": format_duration(item.get("targetHours")),
            "targetMinutes": to_total_minutes(item.get("targetHours")),
            "overtimeHours": format_signed_minutes(balance_minutes),
            "overtimeMinutes": balance_minutes,
            "regularOvertimeHours": format_signed_minutes(regular_ot_balance_mins),
            "regularOvertimeMinutes": regular_ot_balance_mins,
            "restDayOvertimeHours": format_signed_minutes(to_total_minutes(rest_day_ot)),
            "restDayOvertimeMinutes": to_total_minutes(rest_day_ot),
            "publicHolidayOvertimeHours": format_signed_minutes(to_total_minutes(holiday_ot)),
            "publicHolidayOvertimeMinutes": to_total_minutes(holiday_ot),
            "nightOvertimeHours": format_duration(night_ot),
            "nightOvertimeMinutes": to_total_minutes(night_ot),
            "openingBalanceHours": format_signed_minutes(item.get("openingBalanceMinutes")),
            "openingBalanceMinutes": item.get("openingBalanceMinutes", 0),
            "closingBalanceHours": format_signed_minutes(item.get("closingBalanceMinutes")),
            "closingBalanceMinutes": item.get("closingBalanceMinutes", 0),
            "monthly": monthly_buckets,
            "departments": employee.get("departments") or [],
            "employmentType": employee.get("employmentType"),
        })
    return formatted


def calculate_kpi_summary(
    rows: list[dict[str, Any]], mode: str, status: str
) -> dict[str, Any]:
    employee_count = len(rows)

    if mode == "annual":
        total_paid = sum(r.get("paidMinutes", 0) for r in rows)
        total_worked = sum(r.get("actualWorkedMinutes", 0) for r in rows)
        total_target = sum(r.get("targetMinutes", 0) for r in rows)
        total_ot = sum(r.get("overtimeMinutes", 0) for r in rows)
        total_regular_ot = sum(r.get("regularOvertimeMinutes", 0) for r in rows)
        total_rest_day_ot = sum(r.get("restDayOvertimeMinutes", 0) for r in rows)
        total_holiday_ot = sum(r.get("publicHolidayOvertimeMinutes", 0) for r in rows)
        total_night_ot = sum(r.get("nightOvertimeMinutes", 0) for r in rows)
        return {
            "employeeCount": employee_count,
            "totalPaidHours": format_duration(total_paid),
            "totalPaidMinutes": total_paid,
            "totalActualWorkedHours": format_duration(total_worked),
            "totalActualWorkedMinutes": total_worked,
            "totalTargetHours": format_duration(total_target),
            "totalTargetMinutes": total_target,
            "totalOvertimeHours": format_signed_minutes(total_ot),
            "totalOvertimeMinutes": total_ot,
            "totalRegularOvertimeHours": format_signed_minutes(total_regular_ot),
            "totalRestDayOvertimeHours": format_signed_minutes(total_rest_day_ot),
            "totalPublicHolidayOvertimeHours": format_signed_minutes(total_holiday_ot),
            "totalNightOvertimeHours": format_duration(total_night_ot),
        }

    total_target = sum(r.get("targetMinutes", 0) for r in rows)
    total_ot = sum(r.get("overtimeMinutes", 0) for r in rows)
    total_regular_ot = sum(r.get("regularOvertimeMinutes", 0) for r in rows)
    total_rest_day_ot = sum(r.get("restDayOvertimeMinutes", 0) for r in rows)
    total_holiday_ot = sum(r.get("publicHolidayOvertimeMinutes", 0) for r in rows)
    total_night_ot = sum(r.get("nightOvertimeMinutes", 0) for r in rows)

    if status == "PENDING":
        total_awaiting = sum(r.get("hoursAwaitingApprovalMinutes", 0) for r in rows)
        return {
            "employeeCount": employee_count,
            "totalHoursAwaitingApproval": format_duration(total_awaiting),
            "totalHoursAwaitingApprovalMinutes": total_awaiting,
            "totalTargetHours": format_duration(total_target),
            "totalTargetMinutes": total_target,
            "totalProjectedOvertimeHours": format_signed_minutes(total_ot),
            "totalProjectedOvertimeMinutes": total_ot,
            "totalRegularOvertimeHours": format_signed_minutes(total_regular_ot),
            "totalRestDayOvertimeHours": format_signed_minutes(total_rest_day_ot),
            "totalPublicHolidayOvertimeHours": format_signed_minutes(total_holiday_ot),
            "totalProjectedNightOvertimeHours": format_duration(total_night_ot),
        }

    total_approved = sum(r.get("approvedMinutes", 0) for r in rows)
    return {
        "employeeCount": employee_count,
        "totalApprovedHours": format_duration(total_approved),
        "totalApprovedMinutes": total_approved,
        "totalTargetHours": format_duration(total_target),
        "totalTargetMinutes": total_target,
        "totalOvertimeHours": format_signed_minutes(total_ot),
        "totalOvertimeMinutes": total_ot,
        "totalRegularOvertimeHours": format_signed_minutes(total_regular_ot),
        "totalRestDayOvertimeHours": format_signed_minutes(total_rest_day_ot),
        "totalPublicHolidayOvertimeHours": format_signed_minutes(total_holiday_ot),
        "totalNightOvertimeHours": format_duration(total_night_ot),
    }


def format_employee_detail_summary(
    summary: dict[str, Any], status: str
) -> dict[str, Any]:
    approved_hours = summary.get("approvedHours")
    awaiting_hours = summary.get("hoursAwaitingApproval")
    target_hours = summary.get("targetHours")
    overtime_hours = summary.get("overtimeHours")
    night_ot = summary.get("nightOvertimeHours")
    balance_minutes = summary.get("balanceMinutes")
    rest_day_ot = summary.get("restDayOvertimeHours")
    holiday_ot = summary.get("publicHolidayOvertimeHours")

    overtime_display_mins = (
        to_total_minutes(overtime_hours) if status == "PENDING" and overtime_hours is not None
        else balance_minutes if balance_minutes is not None
        else to_total_minutes(overtime_hours)
    )
    regular_ot_mins = get_regular_overtime_balance_minutes(
        overtime_display_mins, rest_day_ot, holiday_ot
    )

    raw_entries = summary.get("entries")
    entries_list = raw_entries.get("data") if isinstance(raw_entries, dict) else raw_entries
    entries_list = entries_list if isinstance(entries_list, list) else []

    formatted_entries = []
    for entry in entries_list:
        shift = entry.get("shift") or {}
        entry_worked = entry.get("workedHours")
        entry_break = entry.get("breakDurationMinutes")
        entry_ot = entry.get("overtimeHours")
        formatted_entries.append({
            "id": entry.get("id"),
            "entryDate": entry.get("entryDate"),
            "startTime": entry.get("startTime"),
            "endTime": entry.get("endTime"),
            "breakDuration": format_duration(entry_break),
            "workedHours": format_duration(entry_worked),
            "workedMinutes": to_total_minutes(entry_worked),
            "overtimeHours": format_signed_minutes(entry.get("balanceMinutes") if entry.get("balanceMinutes") is not None else to_total_minutes(entry_ot)),
            "shiftName": shift.get("name"),
            "scheduleType": entry.get("scheduleType"),
            "sourceType": entry.get("sourceType"),
            "status": entry.get("status"),
            "workMode": entry.get("workMode"),
            "isPublicHoliday": entry.get("isPublicHoliday", False),
            "capWarning": entry.get("capWarning", False),
            "capBlocked": entry.get("capBlocked", False),
            "notes": entry.get("notes"),
        })

    return {
        "employeeId": summary.get("employeeId"),
        "startDate": summary.get("startDate"),
        "endDate": summary.get("endDate"),
        "status": status,
        "approvedHours": format_duration(approved_hours),
        "hoursAwaitingApproval": format_duration(awaiting_hours),
        "targetHours": format_duration(target_hours),
        "overtimeHours": format_signed_minutes(overtime_display_mins),
        "overtimeMinutes": overtime_display_mins,
        "regularOvertimeHours": format_signed_minutes(regular_ot_mins),
        "restDayOvertimeHours": format_signed_minutes(to_total_minutes(rest_day_ot)),
        "publicHolidayOvertimeHours": format_signed_minutes(to_total_minutes(holiday_ot)),
        "nightOvertimeHours": format_duration(night_ot),
        "complianceViolations": summary.get("complianceViolations") or [],
        "approvedOnSiteWorkingDays": summary.get("approvedOnSiteWorkingDays", 0),
        "approvedRemoteWorkingDays": summary.get("approvedRemoteWorkingDays", 0),
        "entriesCount": len(formatted_entries),
        "entries": formatted_entries,
    }
