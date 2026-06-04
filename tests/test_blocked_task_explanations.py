from visaflow.planning.planner import build_task_plan


def test_blocked_tasks_get_waiting_explanations():
    extracted = {
        "deadlines": [],
        "requested_documents": ["passport copy", "current I-20"],
        "action_items": ["Please confirm once the documents have been uploaded"],
    }

    plan = build_task_plan(extracted)
    blocked = [t for t in plan.tasks if t.status == "blocked"]
    assert len(blocked) >= 1
    assert any("Waiting on" in t.blocking_reason for t in blocked)
