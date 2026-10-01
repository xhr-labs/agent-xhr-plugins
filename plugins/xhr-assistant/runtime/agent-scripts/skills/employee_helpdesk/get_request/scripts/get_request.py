from src.shared.skill_wrapper import run_skill_entry
from src.shared.task_args_cli import CLI_STR


if __name__ == "__main__":
    run_skill_entry("src.application.employee_requests.get_request", [
        {"flag": "--request-id", "dest": "request_id", "type": CLI_STR},
    ], injected_task_args=globals().get("TASK_ARGS"))
