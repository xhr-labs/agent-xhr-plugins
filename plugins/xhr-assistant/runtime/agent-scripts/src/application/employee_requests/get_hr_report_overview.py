from src.application.employee_requests.common import call_json, success, value
from src.core.models.request_context import RequestContext
from src.shared.normalize import clean_text


async def run(task_args, context: RequestContext, http_client):
    args = task_args if isinstance(task_args, dict) else {}
    params = {}
    aliases = {"request_type_id": "requestTypeId", "status_id": "statusId", "requester_department_key": "requesterDepartmentKey", "requester_location_key": "requesterLocationKey", "queue_id": "queueId", "assignee_id": "assigneeId", "first_response_sla_outcome": "firstResponseSlaOutcome", "resolution_sla_outcome": "resolutionSlaOutcome", "ageing_bucket": "ageingBucket"}
    for key, query_key in aliases.items():
        text = clean_text(value(args, key, query_key))
        if text:
            params[query_key] = text
    month = clean_text(value(args, "month"))
    if month:
        params["month"] = month
    assignment = clean_text(value(args, "assignment"))
    if assignment:
        params["assignment"] = assignment
    payload, failure = await call_json(
        http_client, "GET", f"{context.api_base_url}/v1/erequest/backoffice/reports/overview",
        headers=context.headers, params=params,
    )
    if failure:
        return failure
    return success(payload, month=month)
