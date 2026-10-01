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

    async with http_client.session() as client:
        # Step 1: Fetch existing balance to get type_id, current balance and year
        get_endpoint = f"{api_base_url}/v1/to/time-off-balances/{balance_id}"
        try:
            status_code, payload = await request_json(client, "GET", get_endpoint, headers=headers)
        except Exception:
            status_code = 404
            payload = {}

        existing_data = payload.get("data") if isinstance(payload, dict) and isinstance(payload.get("data"), dict) else payload

        if status_code >= 400 or not isinstance(existing_data, dict):
            # Fallback: search by id or timeOffTypeId
            query_endpoint = f"{api_base_url}/v1/to/time-off-balances"
            status_code, payload = await request_json(client, "GET", query_endpoint, params={"id.equals": balance_id}, headers=headers)
            items = payload.get("data") if isinstance(payload, dict) and isinstance(payload.get("data"), list) else []
            if not items:
                status_code, payload = await request_json(client, "GET", query_endpoint, params={"timeOffTypeId.equals": balance_id}, headers=headers)
                items = payload.get("data") if isinstance(payload, dict) and isinstance(payload.get("data"), list) else []
            if items and isinstance(items[0], dict):
                existing_data = items[0]
                balance_id = existing_data.get("id") or balance_id

        emp = existing_data.get("employee") if isinstance(existing_data, dict) and isinstance(existing_data.get("employee"), dict) else {}
        ttype = existing_data.get("time_off_type") if isinstance(existing_data, dict) and isinstance(existing_data.get("time_off_type"), dict) else {}

        time_off_type_id = clean_text(task_args.get("time_off_type_id") or ttype.get("id") or (existing_data.get("time_off_type_id") if isinstance(existing_data, dict) else None) or balance_id)
        employee_id = clean_text(task_args.get("employee_id") or emp.get("id") or (existing_data.get("employee_id") if isinstance(existing_data, dict) else None))
        year = int(task_args.get("year") or (existing_data.get("year") if isinstance(existing_data, dict) else None) or 2026)
        base_balance = float((existing_data.get("current_balance") if isinstance(existing_data, dict) else None) or (existing_data.get("available_balance") if isinstance(existing_data, dict) else None) or (existing_data.get("balance") if isinstance(existing_data, dict) else None) or 0.0)

        new_balance = round(base_balance + amount, 2)

        body = {
            "employee_id": employee_id,
            "time_off_type_id": time_off_type_id,
            "current_balance": new_balance,
            "year": year,
        }

        bulk_endpoint = f"{api_base_url}/v1/to/time-off-balances/bulk"
        try:
            status_code, payload = await request_json(client, "PUT", bulk_endpoint, json_data=[body], headers=headers)
        except Exception as exc:
            return error_result(str(format_error(exc=exc)))

    if status_code >= 400:
        return error_result(str(format_error(payload)))

    return ok_result({
        "status": "ADJUSTED",
        "balance_id": balance_id,
        "amount": amount,
        "new_balance": new_balance,
        "reason": reason,
        "response": payload.get("data") if isinstance(payload, dict) else payload,
    })
