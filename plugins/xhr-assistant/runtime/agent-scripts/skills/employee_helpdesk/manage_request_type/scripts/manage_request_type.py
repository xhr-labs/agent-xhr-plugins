from src.shared.skill_wrapper import run_skill_entry
from src.shared.task_args_cli import CLI_INT, CLI_STR


if __name__ == "__main__":
    run_skill_entry("src.application.employee_requests.manage_request_type", [
        {"flag": "--action", "dest": "action", "type": CLI_STR},
        {"flag": "--request-type-id", "dest": "request_type_id", "type": CLI_STR},
        {"flag": "--version-id", "dest": "version_id", "type": CLI_STR},
        {"flag": "--body-json", "dest": "body_json", "type": CLI_STR},
        {"flag": "--draft-json", "dest": "draft_json", "type": CLI_STR},
        {"flag": "--request-type-key", "dest": "request_type_key", "type": CLI_STR},
        {"flag": "--expected-draft-version", "dest": "expected_draft_version", "type": CLI_STR},
        {"flag": "--cursor", "dest": "cursor", "type": CLI_STR},
        {"flag": "--page-size", "dest": "page_size", "type": CLI_INT},
        {"flag": "--idempotency-key", "dest": "idempotency_key", "type": CLI_STR},
        {"flag": "--if-match", "dest": "if_match", "type": CLI_STR},
    ], injected_task_args=globals().get("TASK_ARGS"))
