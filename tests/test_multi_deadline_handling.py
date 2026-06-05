from datetime import datetime, timedelta
from visaflow.planning.planner import build_task_plan


def test_earliest_deadline_is_marked():
    d1 = (datetime.now() + timedelta(days=3)).strftime("%B %d, %Y")
    d2 = (datetime.now() + timedelta(days=10)).strftime("%B %d, %Y")

    extracted = {
        "deadlines": [d2, d1],
        "requested_documents": [],
        "action_items": [],
    }

    plan = build_task_plan(extracted)
    deadline_tasks = [t.task for t in plan.tasks if t.source == "deadline"]

    assert "[earliest]" in deadline_tasks[0]
