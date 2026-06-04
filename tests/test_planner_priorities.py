from visaflow.planning.planner import build_task_plan


def test_priority_assignment():
    extracted = {
        "deadlines": ["June 3, 2026"],
        "requested_documents": ["bank statement", "proof of enrollment"],
        "action_items": [
            "please upload your documents",
            "please confirm once the materials have been uploaded",
        ],
    }

    plan = build_task_plan(extracted)
    task_map = {task.task: task.priority for task in plan.tasks}

    assert task_map["Track deadline: June 3, 2026"] == "high"
    assert task_map["Prepare document: bank statement"] == "high"
    assert task_map["Complete action: please upload your documents"] == "high"
    assert task_map["Complete action: please confirm once the materials have been uploaded"] == "medium"
