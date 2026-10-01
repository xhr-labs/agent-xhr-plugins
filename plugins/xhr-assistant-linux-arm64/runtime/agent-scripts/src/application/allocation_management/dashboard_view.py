from __future__ import annotations

from typing import Any


MAX_CHART_ROWS = 8


def utilization_value(allocated: float, capacity: float) -> dict[str, float]:
    return {
        "allocatedManMonths": allocated,
        "capacityManMonths": capacity,
        "utilizationRate": allocated / capacity * 100 if capacity > 0 else 0,
    }


def metric_detail_rows(rows):
    result = []
    for row in rows:
        allocated = row.get("allocatedManMonths") or 0
        capacity = row.get("capacityManMonths") or 0
        timesheet = row.get("timesheetManMonths") or 0
        variance = timesheet - allocated
        result.append({
            **row,
            "utilizationRate": allocated / capacity * 100 if capacity > 0 else 0,
            "varianceManMonths": variance,
            "variancePercentage": variance / allocated * 100 if allocated > 0 else 0,
        })
    return [
        row for row in result
        if (row.get("allocatedManMonths") or 0) > 0
        or (row.get("capacityManMonths") or 0) > 0
        or (row.get("timesheetManMonths") or 0) > 0
    ]


def monthly_utilization(summaries):
    departments = {}
    employees = {}
    totals_by_month = {}
    months = [item["month"] for item in summaries]

    for item in summaries:
        month = item["month"]
        data = item["data"]
        allocation = data.get("allocationSummary") or {}
        totals_by_month[month] = utilization_value(
            allocation.get("allocatedManMonths") or 0,
            allocation.get("capacityManMonths") or 0,
        )
        for row in data.get("departmentUtilizationBreakdowns") or []:
            key = str(row.get("id") or row.get("code") or row.get("key") or "")
            target = departments.setdefault(key, {
                "key": key, "label": row.get("label"), "valuesByMonth": {}
            })
            target["valuesByMonth"][month] = utilization_value(
                row.get("allocatedManMonths") or 0,
                row.get("capacityManMonths") or 0,
            )

        employee_month = {}
        for row in data.get("employeeAllocationStatusRows") or []:
            key = str(row.get("employeeId") or "")
            target = employee_month.setdefault(key, {
                "employeeName": row.get("employeeName"),
                "departmentName": row.get("departmentName"),
                "allocatedManMonths": 0,
                "capacityManMonths": 0,
            })
            target["allocatedManMonths"] += row.get("allocatedManMonths") or 0
            target["capacityManMonths"] = max(
                target["capacityManMonths"], row.get("capacityManMonths") or 0
            )
        for key, value in employee_month.items():
            target = employees.setdefault(key, {
                "key": key,
                "employeeName": value["employeeName"],
                "departmentName": value["departmentName"],
                "valuesByMonth": {},
            })
            target["valuesByMonth"][month] = utilization_value(
                value["allocatedManMonths"], value["capacityManMonths"]
            )

    def finish(rows):
        for row in rows:
            values = list(row["valuesByMonth"].values())
            row["total"] = utilization_value(
                sum(value["allocatedManMonths"] for value in values),
                sum(value["capacityManMonths"] for value in values),
            )
        return sorted(rows, key=lambda row: -row["total"]["utilizationRate"])

    total = utilization_value(
        sum(value["allocatedManMonths"] for value in totals_by_month.values()),
        sum(value["capacityManMonths"] for value in totals_by_month.values()),
    )
    return {
        "months": months,
        "departmentRows": finish(list(departments.values())),
        "employeeRows": finish(list(employees.values())),
        "totalByMonth": totals_by_month,
        "total": total,
    }


def chart_breakdown(rows, value_key):
    return [
        {
            "key": row.get("id") or row.get("code") or row.get("key"),
            "label": row.get("label"),
            "value": row.get(value_key) or 0,
        }
        for row in sorted(
            (row for row in rows if (row.get(value_key) or 0) > 0),
            key=lambda row: (-(row.get(value_key) or 0), str(row.get("label") or "")),
        )[:MAX_CHART_ROWS]
    ]


def status_chart(rows, value_key):
    order = {"PLANNED": 0, "UNVERIFIED": 1, "TENTATIVE": 2}

    def status_key(row):
        return str(row.get("code") or row.get("key") or "").replace(
            "STATUS:", ""
        ).upper()

    visible = [row for row in rows if (row.get(value_key) or 0) > 0]
    visible.sort(
        key=lambda row: (
            order.get(status_key(row), len(order)),
            str(row.get("label") or ""),
        )
    )
    return [{
        "key": row.get("id") or row.get("code") or row.get("key"),
        "label": row.get("label"),
        "value": row.get(value_key) or 0,
    } for row in visible]


def project_chart(rows):
    grouped = {}
    for row in rows:
        key = str(row.get("projectId") or "")
        target = grouped.setdefault(key, {
            "key": key, "label": row.get("projectName"), "value": 0
        })
        target["value"] += row.get("allocatedManMonths") or 0
    return sorted(grouped.values(), key=lambda row: (-row["value"], str(row["label"])))[:MAX_CHART_ROWS]


def allocation_by_line(status_project, status_employee, matrix_rows, project_rows):
    def status_table(rows):
        visible = sorted(
            (row for row in rows if (row.get("totalManMonths") or 0) > 0),
            key=lambda row: (-(row.get("totalManMonths") or 0), str(row.get("label") or "")),
        )
        fields = ("plannedManMonths", "unverifiedManMonths", "tentativeManMonths", "totalManMonths")
        return {"rows": visible, "total": {field: sum(row.get(field) or 0 for row in visible) for field in fields}}

    columns = {}
    sources = {}
    for row in matrix_rows:
        allocated_key = str(row.get("allocatedLineKey") or "")
        source_key = str(row.get("sourceLineKey") or "")
        value = row.get("allocatedManMonths") or 0
        columns.setdefault(allocated_key, {"key": allocated_key, "label": row.get("allocatedLineLabel"), "totalManMonths": 0})["totalManMonths"] += value
        source = sources.setdefault(source_key, {"key": source_key, "label": row.get("sourceLineLabel"), "valuesByAllocatedLine": {}, "totalManMonths": 0})
        source["valuesByAllocatedLine"][allocated_key] = source["valuesByAllocatedLine"].get(allocated_key, 0) + value
        source["totalManMonths"] += value
    matrix = {
        "columns": sorted((v for v in columns.values() if v["totalManMonths"] > 0), key=lambda v: -v["totalManMonths"]),
        "rows": sorted((v for v in sources.values() if v["totalManMonths"] > 0), key=lambda v: -v["totalManMonths"]),
        "totalManMonths": sum(v["totalManMonths"] for v in sources.values()),
    }

    projects = {}
    for row in project_rows:
        key = str(row.get("projectId") or "")
        target = projects.setdefault(key, {"key": key, "projectName": row.get("projectName"), "sourceLineManMonths": 0, "ownLineManMonths": 0, "totalManMonths": 0})
        value = row.get("allocatedManMonths") or 0
        if row.get("lineType") == "OWN_LINE":
            target["ownLineManMonths"] += value
        else:
            target["sourceLineManMonths"] += value
        target["totalManMonths"] += value
    project_values = sorted((v for v in projects.values() if v["totalManMonths"] > 0), key=lambda v: -v["totalManMonths"])
    return {
        "projectStatus": status_table(status_project),
        "employeeStatus": status_table(status_employee),
        "matrix": matrix,
        "projectSourceVsOwn": {
            "rows": project_values,
            "total": {
                field: sum(row[field] for row in project_values)
                for field in ("sourceLineManMonths", "ownLineManMonths", "totalManMonths")
            },
        },
    }


def timesheet_view(timesheet, months):
    trend_by_month = {row.get("month"): row for row in timesheet.get("monthlyTrendRows") or []}
    trend = [{
        "month": month,
        "allocatedManMonths": (trend_by_month.get(month) or {}).get("allocatedManMonths", 0),
        "timesheetManMonths": (trend_by_month.get(month) or {}).get("timesheetManMonths", 0),
    } for month in months]
    by_line = sorted(timesheet.get("lineComparisonRows") or [], key=lambda row: -((row.get("allocatedManMonths") or 0) + (row.get("timesheetManMonths") or 0)))[:MAX_CHART_ROWS]
    details = metric_detail_rows(timesheet.get("projectDetailRows") or [])
    by_project = {}
    for row in details:
        key = str(row.get("projectId") or row.get("projectCode") or "")
        target = by_project.setdefault(key, {"key": key, "label": row.get("projectName"), "allocatedManMonths": 0, "timesheetManMonths": 0})
        target["allocatedManMonths"] += row.get("allocatedManMonths") or 0
        target["timesheetManMonths"] += row.get("timesheetManMonths") or 0
    project_comparison = sorted(by_project.values(), key=lambda row: -(row["allocatedManMonths"] + row["timesheetManMonths"]))[:MAX_CHART_ROWS]

    matrix_rows = {}
    total_by_month = {month: {"allocatedManMonths": 0, "timesheetManMonths": 0, "varianceManMonths": 0} for month in months}
    for row in timesheet.get("projectMonthRows") or []:
        key = str(row.get("projectId") or row.get("projectCode") or "")
        target = matrix_rows.setdefault(key, {"key": key, "projectCode": row.get("projectCode"), "projectName": row.get("projectName"), "valuesByMonth": {}})
        value = target["valuesByMonth"].setdefault(row.get("month"), {"allocatedManMonths": 0, "timesheetManMonths": 0, "varianceManMonths": 0})
        allocated = row.get("allocatedManMonths") or 0
        actual = row.get("timesheetManMonths") or 0
        value["allocatedManMonths"] += allocated
        value["timesheetManMonths"] += actual
        value["varianceManMonths"] = value["timesheetManMonths"] - value["allocatedManMonths"]
        month_total = total_by_month.setdefault(
            row.get("month"),
            {"allocatedManMonths": 0, "timesheetManMonths": 0, "varianceManMonths": 0},
        )
        month_total["allocatedManMonths"] += allocated
        month_total["timesheetManMonths"] += actual
        month_total["varianceManMonths"] = (
            month_total["timesheetManMonths"]
            - month_total["allocatedManMonths"]
        )
    for row in matrix_rows.values():
        values = list(row["valuesByMonth"].values())
        row["total"] = {"allocatedManMonths": sum(v["allocatedManMonths"] for v in values), "timesheetManMonths": sum(v["timesheetManMonths"] for v in values)}
        row["total"]["varianceManMonths"] = row["total"]["timesheetManMonths"] - row["total"]["allocatedManMonths"]
    matrix_values = sorted(matrix_rows.values(), key=lambda row: -(row["total"]["allocatedManMonths"] + row["total"]["timesheetManMonths"]))
    total = {"allocatedManMonths": sum(v["allocatedManMonths"] for v in total_by_month.values()), "timesheetManMonths": sum(v["timesheetManMonths"] for v in total_by_month.values())}
    total["varianceManMonths"] = total["timesheetManMonths"] - total["allocatedManMonths"]
    return {"trend": trend, "comparisonByLine": by_line, "comparisonByProject": project_comparison, "projectDetail": details, "projectMonthMatrix": {"months": months, "rows": matrix_values, "totalByMonth": total_by_month, "total": total}}
