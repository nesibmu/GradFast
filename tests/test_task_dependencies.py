from visaflow.planning.planner import build_task_plan


def test_upload_and_confirm_depend_on_documents():
    extracted = {
        "deadlines": ["June 3, 2026"],
        "requested_documents": ["bank statement", "passport copy"],
        "action_items": [
            "please upload your documents through the student portal",
            "please confirm once the materials have been uploaded",
        ],
    }

    plan = build_task_plan(extracted)

    upload_task = None
    confirm_task = None
    for task in plan.tasks:
        if "upload your documents" in task.task.lower():
            upload_task = task
        if "please confirm" in task.task.lower():
            confirm_task = task

    assert upload_task is not None
    assert confirm_task is not None
    assert "Prepare document: bank statement" in upload_task.depends_on
    assert "Prepare document: passport copy" in confirm_task.depends_on
