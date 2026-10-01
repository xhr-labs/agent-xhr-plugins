from src.shared.skill_wrapper import run_skill_entry
from src.shared.task_args_cli import CLI_STR


if __name__ == "__main__":
    run_skill_entry("src.application.employee_requests.manage_request_privacy", [
        {"flag": "--action", "dest": "action", "type": CLI_STR},
        {"flag": "--request-id", "dest": "request_id", "type": CLI_STR},
        {"flag": "--operation-id", "dest": "operation_id", "type": CLI_STR},
        {"flag": "--hold-id", "dest": "hold_id", "type": CLI_STR},
        {"flag": "--body-json", "dest": "body_json", "type": CLI_STR},
        {"flag": "--idempotency-key", "dest": "idempotency_key", "type": CLI_STR},
        {"flag": "--if-match", "dest": "if_match", "type": CLI_STR},
    ], injected_task_args=globals().get("TASK_ARGS"))
