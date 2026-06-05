from visaflow.drafting.drafter import (
    generate_next_step_summary,
    generate_action_checklist,
    draft_response_with_mode,
)
from visaflow.schemas import Plan, PlannedTask


def test_summary_and_drafts_feel_more_specific():
    plan = Plan(
        tasks=[
            PlannedTask(task="Track deadline: June 15, 2026", status="urgent", priority="high"),
            PlannedTask(task="Prepare document: signed housing agreement", status="ready", priority="high"),
            PlannedTask(task="Compile and upload requested document packet", status="blocked", priority="high"),
        ]
    )

    summary = generate_next_step_summary(plan)
    checklist = generate_action_checklist(plan)
    enhanced = draft_response_with_mode(plan, enhanced=True)

    assert "Immediate priorities:" in summary
    assert "Action checklist" in checklist
    assert "I will prioritize these first:" in enhanced
