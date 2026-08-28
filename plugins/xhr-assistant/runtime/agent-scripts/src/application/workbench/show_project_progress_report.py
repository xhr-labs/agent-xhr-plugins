from __future__ import annotations

from typing import Any

from src.core.interfaces.http_client import HttpClient
from src.core.models.request_context import RequestContext
from src.shared.normalize import clean_text, is_uuid
from src.shared.result import error_result, ok_result


def _normalize_args(task_args: dict[str, Any]) -> dict[str, Any]:
    task_args = task_args if isinstance(task_args, dict) else {}
    return {
        "project_id": clean_text(task_args.get("project_id") or task_args.get("projectId")),
        "sprint_id": clean_text(task_args.get("sprint_id") or task_args.get("sprintId")),
        "from_date": clean_text(task_args.get("from_date") or task_args.get("fromDate")),
        "to_date": clean_text(task_args.get("to_date") or task_args.get("toDate")),
    }


async def run(task_args: Any, context: RequestContext, http_client: HttpClient) -> dict[str, Any]:
    api_base_url = context.api_base_url
    headers = context.headers

    args = _normalize_args(task_args)
    project_id = args["project_id"]
    sprint_id = args["sprint_id"]
    from_date = args["from_date"]
    to_date = args["to_date"]

    if not project_id:
        return error_result("project_id is required")
    if not is_uuid(project_id):
        return error_result("project_id must be a valid UUID")

    if sprint_id:
        if not is_uuid(sprint_id):
            return error_result("sprint_id must be a valid UUID")
        url = f"{api_base_url}/v1/pm/projects/{project_id}/sprints/{sprint_id}/report"
        insight_url = f"{api_base_url}/v1/pm/projects/{project_id}/sprints/{sprint_id}/insights"

        async with http_client.session() as client:
            resp_report = await client.get(url, headers=headers)
            resp_insight = await client.get(insight_url, headers=headers)

        report_data = resp_report.json().get("data") if resp_report.status_code < 300 and isinstance(resp_report.json(), dict) else resp_report.json() if resp_report.status_code < 300 else {}
        insight_data = resp_insight.json().get("data") if resp_insight.status_code < 300 and isinstance(resp_insight.json(), dict) else resp_insight.json() if resp_insight.status_code < 300 else {}

        return ok_result({
            "project_id": project_id,
            "sprint_id": sprint_id,
            "report": report_data,
            "insights": insight_data,
        })

    # Project summary report
    params: dict[str, Any] = {"projectId": project_id}
    if from_date:
        params["fromDate"] = from_date
    if to_date:
        params["toDate"] = to_date

    url = f"{api_base_url}/v1/pm/reports/workbench/summary"

    async with http_client.session() as client:
        response = await client.get(url, params=params, headers=headers)

    try:
        body = response.json()
    except Exception:
        body = {}

    data = body.get("data") if isinstance(body, dict) and "data" in body else body

    return ok_result({
        "project_id": project_id,
        "summary": data,
        "from_date": from_date,
        "to_date": to_date,
    })
