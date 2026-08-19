from __future__ import annotations

import re


UUID_PATTERN = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$",
    re.IGNORECASE,
)


def display_rows(rows):
    grouped = {}
    for row in rows or []:
        label = str(row.get("label") or "").strip()
        code = str(row.get("code") or "").strip()
        unassigned = not label or UUID_PATTERN.fullmatch(label)
        label = code if unassigned and code and not UUID_PATTERN.fullmatch(code) else label
        if not label or UUID_PATTERN.fullmatch(label):
            label = "Unassigned"
        if label not in grouped:
            grouped[label] = {**row, "label": label}
            continue
        target = grouped[label]
        for key in (
            "totalHeadcount", "activeHeadcount", "newHiresCount",
            "offboardedCount", "netHeadcountChange",
        ):
            target[key] = (target.get(key) or 0) + (row.get(key) or 0)
    return list(grouped.values())


def structure_items(rows):
    return [
        {"label": row.get("label"), "value": row.get("activeHeadcount") or 0}
        for row in sorted(
            (row for row in display_rows(rows) if (row.get("activeHeadcount") or 0) > 0),
            key=lambda row: -(row.get("activeHeadcount") or 0),
        )[:5]
    ]


def change_rows(rows, limit):
    visible = [
        row for row in display_rows(rows)
        if (row.get("newHiresCount") or 0) > 0
        or (row.get("offboardedCount") or 0) > 0
    ]
    visible.sort(key=lambda row: (
        -((row.get("newHiresCount") or 0) + (row.get("offboardedCount") or 0)),
        str(row.get("label") or ""),
    ))
    return [{
        "key": row.get("id") or row.get("code") or row.get("key"),
        "label": row.get("label"),
        "newHiresCount": row.get("newHiresCount") or 0,
        "offboardedCount": row.get("offboardedCount") or 0,
        "netHeadcountChange": row.get("netHeadcountChange") or 0,
        "offboardingRate": (
            (row.get("offboardedCount") or 0) / (row.get("totalHeadcount") or 0) * 100
            if (row.get("totalHeadcount") or 0) > 0 else 0
        ),
    } for row in visible[:limit]]


def offboarded_rows(rows):
    visible = [
        row for row in display_rows(rows)
        if (row.get("offboardedCount") or 0) > 0
    ]
    visible.sort(key=lambda row: (
        -(row.get("offboardedCount") or 0), str(row.get("label") or "")
    ))
    return [{"label": row.get("label"), "value": row.get("offboardedCount") or 0} for row in visible[:8]]


def filter_options(rows):
    return sorted([
        {"value": row.get("id"), "label": row.get("label")}
        for row in display_rows(rows)
        if row.get("id") and row.get("label") != "Unassigned"
    ], key=lambda item: str(item["label"]))


def stacked_department_employee_type(departments, employee_types, summaries):
    # Preserve API identity for matching. Display normalization is intentionally
    # not used here because different employee types may share the same label.
    visible_types = [
        row
        for row in employee_types
        if (row.get("activeHeadcount") or 0) > 0
    ]
    series = [{
        "dataKey": f"employeeType{index}",
        "name": row.get("label"),
    } for index, row in enumerate(visible_types)]
    data = []
    for department, summary in zip(departments, summaries):
        point = {"department": department.get("label")}
        breakdowns = summary.get("employeeTypeBreakdowns") or []
        for index, employee_type in enumerate(visible_types):
            key = employee_type.get("id") or employee_type.get("code") or employee_type.get("key")
            match = next((row for row in breakdowns if (row.get("id") or row.get("code") or row.get("key")) == key), None)
            point[f"employeeType{index}"] = (match or {}).get("activeHeadcount", 0)
        data.append(point)
    return {"data": data, "series": series}
