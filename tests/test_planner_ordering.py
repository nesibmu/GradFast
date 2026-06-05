from visaflow.planning.planner import build_task_plan


def test_plan_orders_high_priority_deadlines_first():
    extracted = {
        "deadlines": ["June 3, 2026"],
        "requested_documents": ["bank statement"],
        "action_items": [
            "please confirm once the materials have been uploaded",
            "please upload your documents",
        ],
    }

    plan = build_task_plan(extracted)
    tasks = [task.task for task in plan.tasks]

    assert tasks[0] == "Track deadline: June 3, 2026"
    assert "Prepare document: bank statement" in tasks
    assert "Complete action: please upload your documents" in tasks
