from src.shared.skill_wrapper import run_skill_entry
from src.shared.task_args_cli import CLI_INT, CLI_STR


if __name__ == "__main__":
    run_skill_entry("src.application.employee_requests.list_eligible_assignees", [
        {"flag": "--queue-id", "dest": "queue_id", "type": CLI_STR},
        {"flag": "--search", "dest": "search", "type": CLI_STR},
        {"flag": "--cursor", "dest": "cursor", "type": CLI_STR},
        {"flag": "--page-size", "dest": "page_size", "type": CLI_INT},
    ], injected_task_args=globals().get("TASK_ARGS"))
