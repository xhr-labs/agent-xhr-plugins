from src.shared.skill_wrapper import run_skill_entry
from src.shared.task_args_cli import CLI_STR


if __name__ == "__main__":
    run_skill_entry("src.application.employee_requests.get_hr_report_overview", [
        {"flag": "--month", "dest": "month", "type": CLI_STR},
        {"flag": "--request-type-id", "dest": "request_type_id", "type": CLI_STR},
        {"flag": "--status-id", "dest": "status_id", "type": CLI_STR},
        {"flag": "--priority", "dest": "priority", "type": CLI_STR},
        {"flag": "--requester-department-key", "dest": "requester_department_key", "type": CLI_STR},
        {"flag": "--requester-location-key", "dest": "requester_location_key", "type": CLI_STR},
        {"flag": "--queue-id", "dest": "queue_id", "type": CLI_STR},
        {"flag": "--assignee-id", "dest": "assignee_id", "type": CLI_STR},
        {"flag": "--assignment", "dest": "assignment", "type": CLI_STR},
        {"flag": "--first-response-sla-outcome", "dest": "first_response_sla_outcome", "type": CLI_STR},
        {"flag": "--resolution-sla-outcome", "dest": "resolution_sla_outcome", "type": CLI_STR},
        {"flag": "--ageing-bucket", "dest": "ageing_bucket", "type": CLI_STR},
    ], injected_task_args=globals().get("TASK_ARGS"))
