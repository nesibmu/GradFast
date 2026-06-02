from visaflow.drafting.drafter import generate_recommended_next_action
from visaflow.schemas import Plan, PlannedTask


def test_recommended_next_action_prefers_urgent():
    plan = Plan(
        tasks=[
            PlannedTask(task="Track deadline: June 15, 2026", status="urgent"),
            PlannedTask(task="Prepare document: passport", status="ready"),
        ]
    )
    result = generate_recommended_next_action(plan)
    assert "Track deadline: June 15, 2026" in result
