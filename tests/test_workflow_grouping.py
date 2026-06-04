from visaflow.planning.planner import build_task_plan


def test_workflow_types_are_assigned():
    extracted = {
        "deadlines": ["June 3, 2026"],
        "requested_documents": ["bank statement", "passport copy", "signed housing agreement"],
        "action_items": [
            "please upload your housing contract through the housing portal",
            "please confirm once the materials have been uploaded",
        ],
    }

    plan = build_task_plan(extracted)
    workflow_types = {task.task: task.workflow_type for task in plan.tasks}

    assert workflow_types["Prepare document: bank statement"] == "financial_aid"
    assert workflow_types["Prepare document: passport copy"] == "immigration"
    assert workflow_types["Prepare document: signed housing agreement"] == "housing"
