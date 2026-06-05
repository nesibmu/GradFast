from visaflow.drafting.drafter import generate_ops_handoff
from visaflow.schemas import Plan, PlannedTask


def test_ops_handoff_has_structured_sections():
    plan = Plan(
        tasks=[
            PlannedTask(task="Track deadline: June 15, 2026", status="urgent"),
            PlannedTask(task="Prepare document: passport copy", status="ready"),
        ]
    )
    extracted = {
        "deadlines": ["June 15, 2026"],
        "requested_documents": ["passport copy"],
        "action_items": ["Please confirm once the documents have been uploaded"],
    }

    handoff = generate_ops_handoff(plan, extracted)

    assert "Case snapshot" in handoff
    assert "Extracted requirements" in handoff
    assert "Execution status" in handoff
    assert "Suggested handoff note" in handoff
