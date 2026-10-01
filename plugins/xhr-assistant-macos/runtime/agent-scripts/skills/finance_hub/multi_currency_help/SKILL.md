---
name: finance-hub-multi-currency-help
description: Explain Finance Hub multi-currency display and conversion behavior. Use when the user asks about currencies, conversion rates, chart currency labels, or multi-currency finance data.
---

# Multi Currency Help

## Intent: finance-hub-multi-currency-help
### User request patterns
- explain finance currency conversion
- show multi-currency finance data
- why is this chart in another currency
- review conversion rate behavior
- explain currency labels in Finance Hub

### Retrieval tags
- finance-hub
- multi-currency
- conversion-rate
- charts
- direct-answer

### Answer objective
Explain multi-currency display and conversion cautiously.

### Instructions
- Answer directly without calling executable tools.
- Do not provide financial advice or assert a live exchange rate.

### Direct answer
Open [Finance Hub]({{finance_url}}) to review currency-aware values.

Finance Hub can display financial data with currency-aware values and chart labels. Some views may use dynamic currency information from the underlying data point or configured reporting currency.

If a value looks wrong, check the record currency, configured conversion behavior, reporting period, and whether the source data has the expected exchange-rate information.
