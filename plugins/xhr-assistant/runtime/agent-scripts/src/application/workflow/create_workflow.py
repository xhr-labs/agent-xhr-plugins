from src.core.models.request_context import RequestContext
from src.core.interfaces.http_client import HttpClient
from src.shared.result import ok_result, error_result


async def run(task_args, context: RequestContext, http_client: HttpClient):
    return ok_result({
        "data": "success",
        "meta": None,
        "query": {},
    })
