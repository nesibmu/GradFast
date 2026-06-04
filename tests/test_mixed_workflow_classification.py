from visaflow.planning.planner import build_task_plan


def test_mixed_case_workflow_classification():
    extracted = {
        "deadlines": ["June 15, 2026"],
        "requested_documents": [
            "signed housing agreement",
            "recent bank statement",
            "copy of passport",
            "current I-20",
        ],
        "action_items": [
            "Please confirm once the documents have been uploaded",
            "If you expect any delay, reply to this message as soon as possible",
        ],
    }

    plan = build_task_plan(extracted)
    workflow_map = {task.task: task.workflow_type for task in plan.tasks}

    assert workflow_map["Prepare document: signed housing agreement"] == "housing"
    assert workflow_map["Prepare document: recent bank statement"] == "financial_aid"
    assert workflow_map["Prepare document: copy of passport"] == "immigration"
    assert workflow_map["Prepare document: current I-20"] == "immigration"
