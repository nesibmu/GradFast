from visaflow.drafting.drafter import (
    generate_next_step_summary,
    generate_action_checklist,
    generate_ops_handoff,
)
from visaflow.schemas import Plan


def test_weak_input_fallback_outputs_are_useful():
    plan = Plan(tasks=[])

    summary = generate_next_step_summary(plan)
    checklist = generate_action_checklist(plan)
    ops = generate_ops_handoff(plan, {"deadlines": [], "requested_documents": [], "action_items": []})

    assert "does not contain enough structured detail" in summary.lower()
    assert "ask for a clearer request" in checklist.lower()
    assert "no structured items were extracted" in ops.lower()
