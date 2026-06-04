from datetime import datetime, timedelta
from visaflow.planning.planner import build_task_plan


def test_due_soon_deadline_ranks_highest():
    near_date = (datetime.now() + timedelta(days=2)).strftime("%B %d, %Y")
    extracted = {
        "deadlines": [near_date],
        "requested_documents": ["passport copy"],
        "action_items": ["Please confirm once the documents have been uploaded"],
    }

    plan = build_task_plan(extracted)
    assert plan.tasks[0].source == "deadline"
    assert plan.tasks[0].urgency_score >= plan.tasks[1].urgency_score
