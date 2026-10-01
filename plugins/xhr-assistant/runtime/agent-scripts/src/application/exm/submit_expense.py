"""Submit a new expense request for the caller.

Mirrors the ``Submit Expense`` dialog of the Expense Management app. Receipts cannot be
uploaded through chat, so this tool only accepts document ids that already exist in the
platform document store (``--documents-json``); the normal flow is for the user to upload
the receipt in the app.
"""

from __future__ import annotations

from typing import Any

from src.application.exm.common import (
    as_args,
    base_url,
    call_json,
    entity_result,
    iso_date,
    parse_json_array,
    require_uuid,
    unwrap_list,
    value,
    write_headers,
)
from src.core.interfaces.http_client import HttpClient
from src.core.models.request_context import RequestContext
from src.shared.normalize import clean_float, clean_text
from src.shared.result import error_result


DOCUMENT_TYPES = ("EXPENSE_RECEIPT", "EXPENSE_INVOICE")


def _documents(raw: Any) -> tuple[list[dict[str, Any]] | None, dict[str, Any] | None]:
    items, error = parse_json_array(raw, "documents_json")
    if error:
        return None, error
    if items is None:
        return None, None

    documents: list[dict[str, Any]] = []
    for item in items:
        if not isinstance(item, dict):
            return None, error_result(
                "documents_json_invalid: each entry must be an object with documentId and documentType."
            )
        document_id = clean_text(item.get("documentId") or item.get("document_id"))
        if not document_id:
            return None, error_result("documents_json_invalid: documentId is required on every entry.")
        document_type = clean_text(item.get("documentType") or item.get("document_type")) or "EXPENSE_RECEIPT"
        if document_type.upper() not in DOCUMENT_TYPES:
            return None, error_result(
                f"documents_json_invalid: documentType '{document_type}'. Allowed: {', '.join(DOCUMENT_TYPES)}."
            )
        documents.append({"document_id": document_id, "document_type": document_type.upper()})
    return documents, None


_ITEM_KEY_MAP = {
    "lineNumber": "line_number",
    "expenseDate": "expense_date",
    "categoryId": "category_id",
    "exchangeRate": "exchange_rate",
    "clientId": "client_id",
    "clientNameSnapshot": "client_name_snapshot",
    "projectId": "project_id",
    "projectNameSnapshot": "project_name_snapshot",
    "costCenterId": "cost_center_id",
    "paymentMethod": "payment_method",
    "attendeeCount": "attendee_count",
    "tripId": "trip_id",
    "distanceUnit": "distance_unit",
    "flightCabinClass": "flight_cabin_class",
}


def _items(raw: list[Any] | None) -> tuple[list[dict[str, Any]] | None, dict[str, Any] | None]:
    """Accept camelCase or snake_case item keys and emit the snake_case the backend wants."""
    if raw is None:
        return None, None
    normalized: list[dict[str, Any]] = []
    for index, item in enumerate(raw):
        if not isinstance(item, dict):
            return None, error_result(f"items_json_invalid: line {index} must be a JSON object.")
        line: dict[str, Any] = {}
        for key, item_value in item.items():
            if key == "receipt" and isinstance(item_value, dict):
                receipt_id = clean_text(item_value.get("documentId") or item_value.get("document_id"))
                receipt_type = clean_text(
                    item_value.get("documentType") or item_value.get("document_type")
                ) or "EXPENSE_RECEIPT"
                if not receipt_id:
                    return None, error_result(
                        f"items_json_invalid: line {index} has a receipt without a documentId."
                    )
                line["receipt"] = {"document_id": receipt_id, "document_type": receipt_type.upper()}
                continue
            line[_ITEM_KEY_MAP.get(key, key)] = item_value
        normalized.append(line)
    return normalized, None

async def _reimbursement_currency(context: RequestContext, http_client: HttpClient):
    """Resolve the currency the caller is reimbursed in.

    The micro-app reads it from the platform context (`employeeLocationId` -> work location
    currency), which is not available to a script. `/company/locations` gives the same data,
    but only one configured location makes the answer unambiguous. With several locations the
    caller's own location cannot be determined here, so the tool refuses instead of guessing a
    currency and filing a wrong reimbursement amount.
    """
    payload, failure = await call_json(
        http_client,
        "GET",
        f"{base_url(context)}/company/locations",
        headers=context.headers,
        feature="read the company work locations",
    )
    if failure:
        return None, failure

    currencies: list[str] = []
    for location in unwrap_list(payload):
        if not isinstance(location, dict):
            continue
        code = clean_text(location.get("currency"))
        if code and code.upper() not in currencies:
            currencies.append(code.upper())

    if len(currencies) == 1:
        return currencies[0], None
    if not currencies:
        return None, error_result(
            "reimbursement_currency_unknown: no work location currency is configured. "
            "Ask the user to submit this expense in the Expense Management app."
        )
    return None, error_result(
        "reimbursement_currency_ambiguous: the company has work locations in "
        f"{', '.join(currencies)} and this tool cannot tell which one applies to the caller. "
        "Ask the user to submit this expense in the Expense Management app, where the form "
        "resolves their own work location."
    )


async def run(task_args, context: RequestContext, http_client: HttpClient):
    args = as_args(task_args)

    name = clean_text(value(args, "name", "title"))
    if not name:
        return error_result("name_required: pass --name with the expense name the user confirmed.")

    expense_date, error = iso_date(value(args, "expense_date", "expenseDate"), "expense_date")
    if error:
        return error
    if not expense_date:
        return error_result("expense_date_required: pass --expense-date YYYY-MM-DD.")

    category_id, error = require_uuid(
        value(args, "category_id", "categoryId"),
        "category_id",
        lookup_hint="skills/exm/list_expense_categories",
    )
    if error:
        return error

    amount = clean_float(value(args, "amount"))
    if amount is None or amount <= 0:
        return error_result("amount_invalid: pass --amount with a number greater than 0.")

    currency = clean_text(value(args, "currency"))
    if not currency:
        return error_result("currency_required: pass --currency as a 3-letter ISO code, for example USD.")
    currency = currency.upper()

    exchange_rate = clean_float(value(args, "exchange_rate", "exchangeRate"))
    if exchange_rate is not None and exchange_rate <= 0:
        return error_result("exchange_rate_invalid: the rate must be greater than 0.")

    documents, error = _documents(value(args, "documents_json", "documentsJson"))
    if error:
        return error

    raw_items, error = parse_json_array(value(args, "items_json", "itemsJson"), "items_json")
    if error:
        return error
    items, error = _items(raw_items)
    if error:
        return error

    reimbursement_currency, failure = await _reimbursement_currency(context, http_client)
    if failure:
        return failure

    # The app records an expense in the REIMBURSEMENT currency: `amount`/`currency` carry
    # what the employee is paid, `exchange_rate` the rate used, and the original amount
    # survives on the item line. Sending the foreign amount at the top level would file a
    # financially wrong claim, so convert here exactly as the Submit Expense dialog does.
    submitted_amount = amount
    submitted_currency = currency
    if currency != reimbursement_currency:
        if exchange_rate is None:
            return error_result(
                f"exchange_rate_required: this expense is in {currency} but reimbursement is in "
                f"{reimbursement_currency}. Ask the user for the rate they used "
                f"(1 {currency} = ? {reimbursement_currency}) and pass --exchange-rate."
            )
        submitted_amount = round(amount * exchange_rate, 2)
        submitted_currency = reimbursement_currency
        if items is None:
            items = [
                {
                    "line_number": 1,
                    "expense_date": expense_date,
                    "category_id": category_id,
                    "amount": amount,
                    "currency": currency,
                    "exchange_rate": exchange_rate,
                }
            ]

    # The EXM backend takes snake_case REQUEST BODIES (query params stay camelCase).
    # The micro-app looks camelCase only because @xhr-labs/sdk converts on the way out;
    # these scripts call the API directly, so the conversion has to happen here.
    body: dict[str, Any] = {
        "name": name,
        "expense_date": expense_date,
        "category_id": category_id,
        "amount": submitted_amount,
        "currency": submitted_currency,
    }
    if exchange_rate is not None:
        body["exchange_rate"] = exchange_rate
    merchant = clean_text(value(args, "merchant"))
    if merchant:
        body["merchant"] = merchant
    description = clean_text(value(args, "description", "notes"))
    if description:
        body["description"] = description
    if documents:
        body["documents"] = documents
    if items:
        body["items"] = items

    payload, failure = await call_json(
        http_client,
        "POST",
        f"{base_url(context)}/expenses",
        headers=write_headers(context, args),
        body=body,
        feature="submit an expense",
    )
    if failure:
        return failure

    return entity_result(payload, submitted=True)
