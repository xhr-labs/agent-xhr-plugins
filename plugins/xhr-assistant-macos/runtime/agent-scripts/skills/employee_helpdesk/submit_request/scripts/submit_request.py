from src.shared.skill_wrapper import run_skill_entry
from src.shared.task_args_cli import CLI_INT, CLI_STR


if __name__ == "__main__":
    run_skill_entry("src.application.employee_requests.submit_request", [
        {"flag": "--request-type-id", "dest": "request_type_id", "type": CLI_STR},
        {"flag": "--request-type-version", "dest": "request_type_version", "type": CLI_INT},
        {"flag": "--answers-json", "dest": "answers_json", "type": CLI_STR},
        {"flag": "--completed-attachment-intent-ids", "dest": "completed_attachment_intent_ids", "type": CLI_STR},
        {"flag": "--idempotency-key", "dest": "idempotency_key", "type": CLI_STR},
    ], injected_task_args=globals().get("TASK_ARGS"))
