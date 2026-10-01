from src.shared.skill_wrapper import run_skill_entry
from src.shared.task_args_cli import CLI_APPEND_STR, CLI_STR


if __name__ == "__main__":
    run_skill_entry(
        "src.application.workbench.add_task_comment",
        [
            {"flag": "--task-id", "dest": "task_id", "type": CLI_STR, "required": True},
            {"flag": "--content", "dest": "content", "type": CLI_STR},
            {"flag": "--document-id", "dest": "document_ids", "type": CLI_APPEND_STR},
        ],
        injected_task_args=globals().get("TASK_ARGS"),
    )
