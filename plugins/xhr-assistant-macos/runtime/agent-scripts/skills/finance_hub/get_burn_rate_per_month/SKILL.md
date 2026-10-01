---
name: finance-hub-get-burn-rate-per-month
description: Get Finance Hub burn rate per month for a target year. Use when the user wants monthly expense or burn reporting and the agent should execute skills/finance_hub/get_burn_rate_per_month/scripts/get_burn_rate_per_month.py.
---

# Get burn rate per month

This file is an executable leaf skill entrypoint.

## Runtime entrypoint
- Execute `skills/finance_hub/get_burn_rate_per_month/scripts/get_burn_rate_per_month.py`.
- Do not search for another child skill under this directory.

## Intent Map

### User request patterns
- What’s my current burn rate per month?
- burn rate
- What are my top 3 cost drivers?
- Why did my burn increase in the last few months?
- What is the average monthly burn rate for 2025?
- What is the median burn rate (to avoid outliers)
- What was the highest burn month and why?
- What was the lowest burn month?
- How much did we spend YTD?
- How much did we spend in Q1 / Q2 / Q3 / Q4?
- What is the most expensive category overall?
- What % of total burn is Salary
- Which categories are one-off vs recurring?
- What is the MoM burn growth rate?
- Which month had the largest MoM increase?
- Which category caused the biggest spike?

### Retrieval tags
- finance-hub
- burn-rate
- spend
- expenses
- analytics

### Answer objective
Run the monthly burn-rate reporting leaf for burn, spend, and expense-trend analytics prompts mapped in the xlsx.

### Instructions
- `year` is optional; omit it to use the runtime default year.
- Use CLI flags for normal execution; the final JSON-object tail exists only as temporary compatibility.
- This report is admin-scoped; rely on tool output for permission denials instead of guessing access.
- Do not invent categories, monthly totals, or currency values; rely on tool output.
- Do not mention internal tool names in the user-facing reply.
- Use this leaf for all burn-rate and expense-trend analytics prompts mapped in the xlsx, including top cost drivers, average/median burn, highest or lowest burn month, YTD or quarterly spend, category mix, one-off vs recurring questions, month-over-month growth, and category spike questions.
- If the user explicitly provides a year, pass `--year <YYYY>`.
- If the user does not specify a year, omit `--year` and let the backend default to the current year.
- Do not ask for a year unless the user needs a different reporting period.

### Execution
```text
python skills/finance_hub/get_burn_rate_per_month/scripts/get_burn_rate_per_month.py [--year <optional YYYY>]
```
