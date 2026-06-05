from visaflow.drafting.drafter import draft_response_with_mode
from visaflow.schemas import Plan, PlannedTask


def test_enhanced_draft_mode_returns_email_style_output():
    plan = Plan(
        tasks=[
            PlannedTask(task="Track deadline: June 3, 2026", priority="high", source="deadline"),
            PlannedTask(task="Prepare document: bank statement", priority="high", source="requested_document"),
        ]
    )

    draft = draft_response_with_mode(plan, enhanced=True)

    assert "Hello," in draft
    assert "I will prioritize the following first:" in draft
    assert "Track deadline: June 3, 2026" in draft
