from src.core.models.request_context import RequestContext
from src.core.interfaces.http_client import HttpClient
from src.shared.normalize import clean_float, clean_text
from src.shared.result import ok_result, error_result
from src.shared.http import format_error, request_json


async def run(task_args, context: RequestContext, http_client: HttpClient):
    api_base_url = context.api_base_url
    headers = context.headers

    task_args = task_args if isinstance(task_args, dict) else {}
    balance_id = clean_text(task_args.get("balance_id") or task_args.get("balanceId") or task_args.get("id"))
    if not balance_id:
        return error_result("balance_id_required")

    amount = clean_float(task_args.get("amount") or task_args.get("adjustment_amount"))
    if amount is None:
        return error_result("amount_required")

    reason = clean_text(task_args.get("reason") or task_args.get("notes") or task_args.get("note"))

    body = {
        "amount": amount,
    }
    if reason:
        body["reason"] = reason

    endpoint = f"{api_base_url}/v1/to/time-off-balances/{balance_id}"

    async with http_client.session() as client:
        try:
            status_code, payload = await request_json(client, "PATCH", endpoint, json_data=body, headers=headers)
        except Exception as exc:
            return error_result(str(format_error(exc=exc)))

    if status_code >= 400:
        return error_result(str(format_error(payload)))

    return ok_result({
        "status": "ADJUSTED",
        "balance_id": balance_id,
        "amount": amount,
        "reason": reason,
        "response": payload.get("data") if isinstance(payload, dict) else payload,
    })
