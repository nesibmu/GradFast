from visaflow.planning.planner import build_task_plan


def test_task_states_are_assigned():
    extracted = {
        "deadlines": ["June 12, 2026"],
        "requested_documents": ["passport", "bank statement"],
        "action_items": [
            "Please confirm once the materials have been uploaded",
            "Please upload your documents through the student portal",
        ],
    }

    plan = build_task_plan(extracted)
    statuses = {task.task: task.status for task in plan.tasks}

    assert statuses["Track deadline: June 12, 2026"] == "urgent"
    assert statuses["Prepare document: passport"] == "ready"
    assert any(status == "blocked" for status in statuses.values())
