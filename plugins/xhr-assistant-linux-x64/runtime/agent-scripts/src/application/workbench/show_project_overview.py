from src.core.models.request_context import RequestContext
from src.core.interfaces.http_client import HttpClient
from src.shared.normalize import clean_int, to_bool
from src.shared.result import ok_result, error_result


def _format_project(project):
    if not isinstance(project, dict):
        return None

    owner = project.get("owner") or {}
    status = project.get("status") or {}

    return {
        "project_id": project.get("id"),
        "project_name": project.get("name"),
        "code": project.get("project_code"),
        "owner": owner.get("full_name") or owner.get("email"),
        "start_date": project.get("start_date"),
        "due_date": project.get("due_date"),
        "status": status.get("name"),
        "total_tasks": project.get("total_tasks"),
        "visibility": project.get("project_visibility"),
        "enable_sprint": project.get("enable_sprint") if "enable_sprint" in project else project.get("enableSprint"),
    }


async def run(task_args, context: RequestContext, http_client: HttpClient):
    api_base_url = context.api_base_url
    headers = context.headers

    task_args = task_args if isinstance(task_args, dict) else {}
    recursive = to_bool(task_args.get("recursive"))
    if "recursive" not in task_args and "isRecursive" in task_args:
        recursive = to_bool(task_args.get("isRecursive"))

    page_number = clean_int(task_args.get("page_number"))
    if page_number is None:
        page_number = clean_int(task_args.get("pageNumber"))
    if page_number is None:
        page_number = 0

    page_size = clean_int(task_args.get("page_size"))
    if page_size is None:
        page_size = clean_int(task_args.get("pageSize"))
    if page_size is None:
        page_size = 1000 if recursive else 10

    page_number = max(page_number, 0)
    page_size = min(max(page_size, 1), 1000)

    name = task_args.get("project_name") or task_args.get("projectName")
    if isinstance(name, str):
        trimmed = name.strip()
        lowered = trimmed.lower()
        suffix = " project"
        if lowered.endswith(suffix):
            trimmed = trimmed[: -len(suffix)].rstrip()
        name = trimmed or None
    else:
        name = None

    query_params = {
        "pageNumber": page_number,
        "pageSize": page_size,
    }
    query_output = {
        "page_number": page_number,
        "page_size": page_size,
        "recursive": recursive,
    }

    if name:
        query_params["name"] = name
        query_output["name"] = name

    projects_url = f"{api_base_url}/v1/pm/projects/basic-info"

    async with http_client.session() as client:
        all_projects = []
        final_meta = None
        final_status_code = 200
        pages_fetched = 0
        current_page_number = page_number

        while True:
            current_query_params = {
                **query_params,
                "pageNumber": current_page_number,
                "pageSize": page_size,
            }
            response = await client.get(projects_url, params=current_query_params, headers=headers)
            try:
                payload = response.json()
            except Exception:
                payload = {}

            final_status_code = response.status_code
            pages_fetched += 1

            redirect_to = None
            if isinstance(payload, dict):
                data = payload.get("data")
                if isinstance(data, dict):
                    redirect_to = data.get("redirect_to")

            if redirect_to:
                detail_url = f"{api_base_url}/v1/pm/projects/{redirect_to}"
                detail_response = await client.get(detail_url, headers=headers)

                try:
                    detail_payload = detail_response.json()
                except Exception:
                    detail_payload = {}

                if isinstance(detail_payload, dict):
                    project = detail_payload.get("data")
                    meta = detail_payload.get("meta")
                else:
                    project = None
                    meta = None

                formatted_project = _format_project(project)
                data_output = [formatted_project] if formatted_project else []
                detail_meta = meta if isinstance(meta, dict) else {}
                detail_meta = {
                    **detail_meta,
                    "pages_fetched": pages_fetched,
                    "total_items_returned": len(data_output),
                }

                if detail_response.status_code < 200 or detail_response.status_code >= 300:
                    return error_result(f"Project detail request failed: {detail_response.status_code} {str(detail_payload)}",)

                return ok_result({
                    "redirect_to": redirect_to,
                    "projects": data_output,
                    "meta": detail_meta,
                    "query": query_output,
                })

            if isinstance(payload, dict):
                projects = payload.get("data", []) or []
                meta = payload.get("meta", None)
            else:
                projects = []
                meta = None

            if isinstance(projects, list):
                all_projects.extend(projects)

            final_meta = meta
            has_next = False
            if isinstance(meta, dict):
                has_next = bool(meta.get("has_next"))

            if response.status_code >= 400 or not recursive or not has_next:
                break
            current_page_number += 1

    formatted_projects = []
    for project in all_projects:
        formatted = _format_project(project)
        if formatted is not None:
            formatted_projects.append(formatted)

    enriched_meta = final_meta if isinstance(final_meta, dict) else {}
    enriched_meta = {
        **enriched_meta,
        "pages_fetched": pages_fetched,
        "total_items_returned": len(formatted_projects),
    }

    if final_status_code < 200 or final_status_code >= 300:
        return error_result(f"Projects request failed: {final_status_code}",)

    return ok_result({
        "projects_count": len(formatted_projects),
        "projects": formatted_projects,
        "meta": enriched_meta,
        "query": query_output,
    })
