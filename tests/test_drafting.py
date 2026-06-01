from visaflow.drafting.drafter import draft_response
from visaflow.schemas import Plan, PlannedTask


def test_draft_response_includes_sections():
    plan = Plan(
        tasks=[
            PlannedTask(task="Track deadline: June 3, 2026", priority="high", source="deadline"),
            PlannedTask(task="Complete action: please confirm once uploaded", priority="medium", source="action_item"),
        ]
    )

    draft = draft_response(plan)

    assert "Suggested next steps" in draft
    assert "Urgent:" in draft
    assert "Important follow-up:" in draft
    assert "Draft reply:" in draft


def test_draft_response_handles_empty_plan():
    draft = draft_response(Plan(tasks=[]))
    assert "No immediate action items were identified." in draft
