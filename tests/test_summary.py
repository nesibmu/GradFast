from visaflow.drafting.drafter import generate_next_step_summary
from visaflow.schemas import Plan, PlannedTask


def test_summary_includes_high_priority_tasks():
    plan = Plan(
        tasks=[
            PlannedTask(task="Track deadline: June 3, 2026", priority="high", source="deadline"),
            PlannedTask(task="Prepare document: bank statement", priority="high", source="requested_document"),
            PlannedTask(task="Complete action: please confirm once uploaded", priority="medium", source="action_item"),
        ]
    )

    summary = generate_next_step_summary(plan)

    assert "Next-step summary:" in summary
    assert "Handle these first:" in summary
    assert "Track deadline: June 3, 2026" in summary
    assert "Prepare document: bank statement" in summary
    assert "Then follow up on:" in summary


def test_summary_handles_empty_plan():
    summary = generate_next_step_summary(Plan(tasks=[]))
    assert "No immediate action items were identified." in summary
