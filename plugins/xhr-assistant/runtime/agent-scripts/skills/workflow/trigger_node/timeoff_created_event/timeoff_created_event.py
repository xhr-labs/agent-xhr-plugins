import asyncio
import src.application.workflow.timeoffCreatedEvent as tool
from src.infrastructure.di.singleton_container import container


if __name__ == "__main__":
    task_args = globals().get("TASK_ARGS")
    context = container.get_request_context()
    http_client = container.get_http_client()
    asyncio.run(tool.run(task_args, context, http_client))
