---
name: get-employee-distribution-by-department
description: Show the complete employee headcount distribution by department and return a PieChart action for the Agent UI.
side_effect: read
frontend_action: true
frontend_action_tool_name: exec
frontend_action_payload_mode: exec_path_args
frontend_action_execution_policy: always
---

## Intent: get-employee-distribution-by-department
### User request patterns
- show employee distribution by department
- show headcount by department
- show how many employees are in each department
- display the department employee breakdown
- visualize employees by department
- compare employee counts across departments

### Retrieval tags
- employee
- department
- headcount
- distribution
- workforce-report
- pie-chart

### Answer objective
Answer company-wide department distribution questions with the complete workforce report data and a rendered pie chart.

### Instructions
- Use this skill for a complete distribution across all departments. Do not use the limited dashboard presentation model for this request.
- Default to active employees. Use `headcount_scope=TOTAL` only when the user asks for all employee records, including inactive or offboarded records.
- Default `month` to the current month. Use the requested `YYYY-MM` month for historical questions.
- Preserve every department returned by the workforce report. Do not truncate to a top-five or top-eight list, merge departments, or invent missing departments.
- Explain the total and the count for each department using the returned data. Do not expose internal IDs, endpoint paths, or raw JSON.
- Always execute this skill's tool for a department distribution request. The tool result emits the `render_piechart` action that renders the chart in the frontend.
- After execution, do not print, quote, or serialize the action payload or tool result. Return only a concise natural-language summary; the chart action is delivered separately to the frontend.
- If the report is empty, explain that no matching employees were found for the selected month and scope; do not imply the request failed.
- If the tool reports an error, explain that the workforce report could not be loaded and ask the user to retry. Do not expose backend error details.

### Frontend chart response contract

The Agent UI renders charts from a frontend action returned by the tool. Return the action in this exact shape:

```python
return ok_result(
    {
        "action": "render_piechart",
        "content": {
            "data": [
                {"name": "Engineering", "value": 12, "color": "#5B8DEF"}
            ],
            "height": 300,
            "legendAlign": "start",
            "legendPosition": "right",
            "showLegend": True,
            "showLegendValues": True,
            "showLegendPercentages": True,
        },
    }
)
```

The `action` value selects the chart. Put only JSON-serializable values in `content`; do not return React nodes, Python functions, callbacks, or serialized JSON strings. The current tool in this skill uses `render_piechart`. The Agent UI also supports these action names for other tools:

| Action | Required content shape |
| --- | --- |
| `render_piechart` | `data`: `{name, value, color}` objects. `value` must be a non-negative number and `color` must be a six-digit hex color. |
| `render_linechart` | `data`: row objects; `series`: `{dataKey, name?, color?}` objects; `xAxisKey`: the row field used for the horizontal axis. Each series needs at least one numeric value. |
| `render_groupedbarchart` | `data`: row objects; `series`: `{dataKey, name?, color?}` objects; `xAxisKey`: the row field used for the horizontal axis. Each series needs at least one numeric value. |
| `render_groupedhorizontalbarchart` | `data`: row objects; `series`: `{dataKey, name?, color?}` objects; `yAxisKey`: the row field used for the vertical labels. Each series needs at least one numeric value. |
| `render_horizontalbarchart` | `data`: `{label, value, color?}` objects. `value` must be a non-negative number. |
| `render_stackedbarchart` | `data`: row objects; `series`: `{dataKey, name?, color?, showLabel?}` objects; `xAxisKey`: the row field used for the horizontal axis. Each series needs at least one numeric value. |
| `render_verticalbarchart` | `data`: `{label, value, color?}` objects. `value` must be a non-negative number. |

Use one of these complete, copyable response examples. Keep the outer `ok_result` envelope, put the action name in `data.action`, and put the chart configuration in `data.content`.

### PieChart — `render_piechart`

Use `{name, value, color}` rows. `value` is the numeric slice size.

```python
return ok_result(
    {
        "action": "render_piechart",
        "content": {
            "data": [
                {"name": "Engineering", "value": 12, "color": "#5B8DEF"},
                {"name": "Operations", "value": 8, "color": "#3D741C"},
                {"name": "Business", "value": 5, "color": "#B87513"},
            ],
            "height": 300,
            "legendPosition": "right",
            "showLegend": True,
            "showLegendValues": True,
            "showLegendPercentages": True,
        },
    }
)
```

### LineChart — `render_linechart`

Use row objects for `data`, list each numeric line in `series`, and point `xAxisKey` to the label field.

```python
return ok_result(
    {
        "action": "render_linechart",
        "content": {
            "data": [
                {"month": "Jan", "total": 85, "technical": 52, "operations": 17},
                {"month": "Feb", "total": 87, "technical": 54, "operations": 17},
                {"month": "Mar", "total": 91, "technical": 56, "operations": 19},
            ],
            "series": [
                {
                    "dataKey": "total",
                    "name": "Total",
                    "color": "#1D1D1F",
                    "strokeWidth": 4,
                    "showValueLabels": True,
                },
                {
                    "dataKey": "technical",
                    "name": "Technical",
                    "color": "#1E5FA8",
                    "strokeWidth": 3,
                },
                {
                    "dataKey": "operations",
                    "name": "Operations",
                    "color": "#3D741C",
                    "showDots": False,
                    "strokeDasharray": "5 4",
                },
            ],
            "title": "Headcount trend",
            "xAxisKey": "month",
            "selectedXAxisValue": "Mar",
            "yAxisDomain": [0, 100],
            "yAxisTicks": [0, 25, 50, 75, 100],
        },
    }
)
```

### GroupedBarChart — `render_groupedbarchart`

Use row objects with one property per bar and set `xAxisKey` to the category field. Use `presentation: "grouped"` when bars should remain side by side.

```python
return ok_result(
    {
        "action": "render_groupedbarchart",
        "content": {
            "data": [
                {"month": "Jan", "income": 8000, "expenditures": 5000},
                {"month": "Feb", "income": 7500, "expenditures": 4500},
                {"month": "Mar", "income": 8200, "expenditures": 5200},
            ],
            "series": [
                {"dataKey": "expenditures", "name": "Expenses", "color": "#FFBB98"},
                {"dataKey": "income", "name": "Income", "color": "#D1DEFF"},
            ],
            "height": 314,
            "presentation": "grouped",
            "xAxisKey": "month",
        },
    }
)
```

### GroupedHorizontalBarChart — `render_groupedhorizontalbarchart`

Use row objects with one property per bar and set `yAxisKey` to the category field. This is the horizontal equivalent of `render_groupedbarchart`.

```python
return ok_result(
    {
        "action": "render_groupedhorizontalbarchart",
        "content": {
            "data": [
                {"productLine": "VG/NMK", "headcount": 20, "fte": 17},
                {"productLine": "NMG", "headcount": 18, "fte": 15.3},
                {"productLine": "Internal", "headcount": 18, "fte": 16.2},
            ],
            "series": [
                {"dataKey": "headcount", "name": "Headcount", "color": "#1E64A8"},
                {"dataKey": "fte", "name": "FTE", "color": "#B7CDE4"},
            ],
            "title": "Headcount and FTE by product line",
            "showLegend": True,
            "showValues": True,
            "yAxisKey": "productLine",
        },
    }
)
```

### HorizontalBarChart — `render_horizontalbarchart`

Use flat `{label, value, color}` rows. Do not wrap these rows in `series`.

```python
return ok_result(
    {
        "action": "render_horizontalbarchart",
        "content": {
            "data": [
                {"label": "Delivery", "value": 18, "color": "#5A4BBB"},
                {"label": "AI", "value": 13, "color": "#5A4BBB"},
                {"label": "NMG", "value": 8, "color": "#3A7614"},
                {"label": "VG/NMK", "value": 7, "color": "#BE7615"},
            ],
            "title": "Employees by source line",
            "showValues": True,
        },
    }
)
```

### StackedBarChart — `render_stackedbarchart`

Use row objects with one property per stack segment. Set `showLabel: True` on a series when its segment should display a value label.

```python
return ok_result(
    {
        "action": "render_stackedbarchart",
        "content": {
            "data": [
                {"division": "BO", "fullTime": 6, "intern": 1, "contractor": 0},
                {"division": "Business", "fullTime": 14, "intern": 4, "contractor": 2},
                {"division": "Delivery", "fullTime": 12, "intern": 3, "contractor": 1},
            ],
            "series": [
                {
                    "dataKey": "fullTime",
                    "name": "Full-time",
                    "color": "#1E64A8",
                    "showLabel": True,
                },
                {
                    "dataKey": "intern",
                    "name": "Intern",
                    "color": "#BE7615",
                    "showLabel": True,
                },
                {"dataKey": "contractor", "name": "Contractor", "color": "#3A7614"},
            ],
            "title": "Employee types by division",
            "xAxisKey": "division",
            "yAxisDomain": [0, 25],
            "yAxisTicks": [0, 5, 10, 15, 20, 25],
        },
    }
)
```

### VerticalBarChart — `render_verticalbarchart`

Use the same flat `{label, value, color}` row shape as the horizontal bar chart, but with a vertical layout.

```python
return ok_result(
    {
        "action": "render_verticalbarchart",
        "content": {
            "data": [
                {"label": "Implementation", "value": 42.5, "color": "#1E64A8"},
                {"label": "Workflow", "value": 27.25, "color": "#3A7614"},
                {"label": "Support", "value": 18, "color": "#BE7615"},
                {"label": "Research", "value": 12.25, "color": "#E84C4F"},
            ],
            "title": "Effort distribution by project type",
            "showValues": True,
            "yAxisDomain": [0, 50],
            "yAxisTicks": [0, 10, 20, 30, 40, 50],
        },
    }
)
```

Chart-specific options are optional. Use only options supported by the selected chart contract, and keep them as native JSON numbers, booleans, arrays, or strings. Do not include `titleIcon`, `valueFormatter`, or other callback props because the tool result crosses the agent boundary as JSON.

### Optional arguments
- `month`: Report month in `YYYY-MM` format. Defaults to the current month.
- `headcount_scope`: `ACTIVE` (default) or `TOTAL`.

### Execution
```text
python skills/employee/get_employee_distribution_by_department/scripts/get_employee_distribution_by_department.py [--month <YYYY-MM>] [--headcount-scope ACTIVE|TOTAL]
```
