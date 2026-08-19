import uuid
import secrets
from src.shared.result import ok_result, error_result


def _generate_step_id_fragment():
    return secrets.token_hex(3)


def _generate_action_id_fragment():
    return str(uuid.uuid4()).replace("-", "_")


def generate_workflow_ids(step_id, action_id):
    try:
        step_count = int(step_id)
    except Exception:
        step_count = 0
    try:
        action_count = int(action_id)
    except Exception:
        action_count = 0

    step_count = max(step_count, 0)
    action_count = max(action_count, 0)

    step_ids = [_generate_step_id_fragment() for _ in range(step_count)]
    action_ids = [_generate_action_id_fragment() for _ in range(action_count)]

    return {
        "step_ids": step_ids,
        "action_ids": action_ids,
    }


async def run(task_args, context=None, http_client=None):
    task_args = task_args if isinstance(task_args, dict) else {}
    step_id = task_args.get("step_id", 0)
    action_id = task_args.get("action_id", 0)
    payload = generate_workflow_ids(step_id, action_id)
    return ok_result({
        "data": payload,
        "meta": None,
        "query": {"step_id": step_id, "action_id": action_id},
    })
