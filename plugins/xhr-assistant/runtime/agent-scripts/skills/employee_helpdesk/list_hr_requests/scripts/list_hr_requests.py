from src.shared.skill_wrapper import run_skill_entry
from src.shared.task_args_cli import CLI_INT, CLI_STR


if __name__ == "__main__":
    run_skill_entry("src.application.employee_requests.list_hr_requests", [
        {"flag": "--queue-id", "dest": "queue_id", "type": CLI_STR},
        {"flag": "--request-type-id", "dest": "request_type_id", "type": CLI_STR},
        {"flag": "--status-key", "dest": "status_key", "type": CLI_STR},
        {"flag": "--priority", "dest": "priority", "type": CLI_STR},
        {"flag": "--assignee-id", "dest": "assignee_id", "type": CLI_STR},
        {"flag": "--assignment", "dest": "assignment", "type": CLI_STR},
        {"flag": "--sla-risk", "dest": "sla_risk", "type": CLI_STR},
        {"flag": "--view", "dest": "view", "type": CLI_STR},
        {"flag": "--search", "dest": "search", "type": CLI_STR},
        {"flag": "--created-from", "dest": "created_from", "type": CLI_STR},
        {"flag": "--created-to", "dest": "created_to", "type": CLI_STR},
        {"flag": "--sort", "dest": "sort", "type": CLI_STR},
        {"flag": "--order", "dest": "order", "type": CLI_STR},
        {"flag": "--cursor", "dest": "cursor", "type": CLI_STR},
        {"flag": "--page-size", "dest": "page_size", "type": CLI_INT},
    ], injected_task_args=globals().get("TASK_ARGS"))
