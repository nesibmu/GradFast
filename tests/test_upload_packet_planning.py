from visaflow.planning.planner import build_task_plan


def test_upload_packet_task_is_added_for_document_sets():
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
        ],
    }

    plan = build_task_plan(extracted)
    tasks = [task.task for task in plan.tasks]

    assert "Compile and upload requested document packet" in tasks

    confirm_tasks = [task for task in plan.tasks if "please confirm" in task.task.lower()]
    assert len(confirm_tasks) == 1
    assert "Compile and upload requested document packet" in confirm_tasks[0].depends_on
