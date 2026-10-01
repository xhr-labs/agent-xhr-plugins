from src.shared.skill_wrapper import run_skill_entry
from src.shared.task_args_cli import CLI_STR


if __name__ == "__main__":
    run_skill_entry("src.application.employee_requests.add_request_message", [
        {"flag": "--request-id", "dest": "request_id", "type": CLI_STR},
        {"flag": "--body", "dest": "body", "type": CLI_STR},
        {"flag": "--client-message-id", "dest": "client_message_id", "type": CLI_STR},
        {"flag": "--if-match", "dest": "if_match", "type": CLI_STR},
        {"flag": "--idempotency-key", "dest": "idempotency_key", "type": CLI_STR},
    ], injected_task_args=globals().get("TASK_ARGS"))
