from visaflow.planning.planner import build_task_plan


def test_shared_admin_language_uses_document_context():
    extracted = {
        "deadlines": [],
        "requested_documents": ["passport copy", "current I-20"],
        "action_items": ["Please confirm once the documents have been uploaded through the student portal"],
    }

    plan = build_task_plan(extracted)
    action_tasks = [t for t in plan.tasks if t.source == "action_item" and "confirm" in t.task.lower()]
    assert len(action_tasks) == 1
    assert action_tasks[0].workflow_type == "immigration"
