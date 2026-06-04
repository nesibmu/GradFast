from visaflow.planning.planner import is_due_soon, build_task_plan
from datetime import datetime, timedelta


def test_due_soon_helper_and_label():
    near_date = (datetime.now() + timedelta(days=3)).strftime("%B %d, %Y")
    far_date = (datetime.now() + timedelta(days=20)).strftime("%B %d, %Y")

    assert is_due_soon(near_date) is True
    assert is_due_soon(far_date) is False

    extracted = {
        "deadlines": [near_date],
        "requested_documents": [],
        "action_items": [],
    }
    plan = build_task_plan(extracted)
    assert "[due soon]" in plan.tasks[0].task
