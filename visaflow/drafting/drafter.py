from visaflow.schemas import Plan


def _top_tasks(tasks, limit=4):
    return [task.task for task in tasks[:limit]]


def generate_recommended_next_action(plan: Plan) -> str:
    if not plan.tasks:
        return "Recommended next action: gather a fuller administrative request before taking action."

    urgent = [task for task in plan.tasks if task.status == "urgent"]
    ready = [task for task in plan.tasks if task.status == "ready"]
    blocked = [task for task in plan.tasks if task.status == "blocked"]

    if urgent:
        return f"Recommended next action: {urgent[0].task}"
    if ready:
        return f"Recommended next action: {ready[0].task}"
    if blocked:
        return f"Recommended next action: unblock {blocked[0].task}"
    return "Recommended next action: review the request again for missing details."


def generate_short_summary(plan: Plan, extracted: dict) -> str:
    deadlines = extracted.get("deadlines", [])
    documents = extracted.get("requested_documents", [])
    actions = extracted.get("action_items", [])

    if not plan.tasks:
        return (
            "Short summary\n\n"
            "- Limited signal detected\n"
            "- No clear workflow generated\n"
            "- Next step: request a fuller message or complete email thread"
        )

    lines = []
    lines.append("Short summary")
    lines.append("")
    lines.append(f"- {generate_recommended_next_action(plan).replace('Recommended next action: ', 'Next action: ')}")
    lines.append(f"- Deadlines: {len(deadlines)}")
    lines.append(f"- Documents: {len(documents)}")
    lines.append(f"- Actions: {len(actions)}")

    urgent = [task.task for task in plan.tasks if task.status == "urgent"]
    if urgent:
        lines.append(f"- Urgent item: {urgent[0]}")

    return "\n".join(lines)


def generate_next_step_summary(plan: Plan) -> str:
    if not plan.tasks:
        return (
            "Recommended next action: gather a fuller administrative request before taking action.\n\n"
            "This message does not contain enough structured detail to build a strong workflow.\n"
            "A better input would usually include a deadline, requested documents, or a specific action."
        )

    urgent = [task for task in plan.tasks if task.status == "urgent"]
    ready = [task for task in plan.tasks if task.status == "ready"]
    blocked = [task for task in plan.tasks if task.status == "blocked"]

    lines = []
    lines.append(generate_recommended_next_action(plan))
    lines.append("")
    lines.append("Here is the current operational picture:")
    lines.append("")

    if urgent:
        lines.append("Immediate priorities:")
        for task in _top_tasks(urgent, limit=3):
            lines.append(f"- {task}")
        deadline_tasks = [task.task for task in urgent if "deadline" in task.task.lower()]
        if len(deadline_tasks) > 1:
            lines.append("- Multiple deadlines were detected, so the earliest deadline should be handled first.")
        lines.append("")

    if ready:
        lines.append("Ready to move forward:")
        for task in _top_tasks(ready, limit=4):
            lines.append(f"- {task}")
        lines.append("")

    if blocked:
        lines.append("Still dependent on earlier steps:")
        for task in _top_tasks(blocked, limit=3):
            lines.append(f"- {task}")

    return "\n".join(lines).strip()


def generate_action_checklist(plan: Plan) -> str:
    if not plan.tasks:
        return (
            "Checklist\n\n"
            "[ ] Ask for a clearer request or full email thread\n"
            "[ ] Look for deadlines, document names, or requested actions\n"
            "[ ] Re-run the workflow once more structured information is available"
        )

    lines = []
    lines.append("Checklist")
    lines.append("")

    for task in plan.tasks:
        label = task.status.upper()
        lines.append(f"[ ] {task.task}  |  {label}")

    return "\n".join(lines)


def generate_task_digest(plan: Plan, extracted: dict) -> str:
    deadlines = extracted.get("deadlines", [])
    urgent = [task for task in plan.tasks if task.status == "urgent"]
    ready = [task for task in plan.tasks if task.status == "ready"]
    blocked = [task for task in plan.tasks if task.status == "blocked"]

    if not plan.tasks:
        return (
            "Task digest\n\n"
            "No concrete tasks were detected from this message.\n\n"
            "Suggested next step:\n"
            "- Ask the sender to clarify what action is needed, what documents are required, and whether there is a deadline."
        )

    lines = []
    lines.append("Task digest")
    lines.append("")
    lines.append(generate_recommended_next_action(plan))
    lines.append("")

    lines.append("Immediate focus")
    if urgent:
        for task in urgent[:3]:
            lines.append(f"- {task.task}")
    elif ready:
        lines.append(f"- {ready[0].task}")
    else:
        lines.append("- Resolve blocked items first.")
    lines.append("")

    lines.append("Ready tasks")
    if ready:
        for task in ready[:5]:
            lines.append(f"- [{task.workflow_type}] {task.task} — urgency {task.urgency_score}")
    else:
        lines.append("- None detected.")
    lines.append("")

    lines.append("Blocked tasks")
    if blocked:
        for task in blocked[:4]:
            line = f"- {task.task}"
            if getattr(task, "blocking_reason", ""):
                line += f" — {task.blocking_reason}"
            lines.append(line)
    else:
        lines.append("- None detected.")
    lines.append("")

    lines.append("Deadlines")
    if deadlines:
        for deadline in deadlines:
            lines.append(f"- {deadline}")
    else:
        lines.append("- No explicit deadline detected.")

    return "\n".join(lines)


def generate_ops_handoff(plan: Plan, extracted: dict) -> str:
    deadlines = extracted.get("deadlines", [])
    documents = extracted.get("requested_documents", [])
    actions = extracted.get("action_items", [])

    urgent = [task.task for task in plan.tasks if task.status == "urgent"]
    ready = [task.task for task in plan.tasks if task.status == "ready"]
    blocked = [task.task for task in plan.tasks if task.status == "blocked"]

    lines = []
    lines.append("Operations handoff")
    lines.append("")
    lines.append(generate_recommended_next_action(plan))
    lines.append("")

    lines.append("Case snapshot")
    lines.append(f"- Deadlines found: {len(deadlines)}")
    lines.append(f"- Requested documents found: {len(documents)}")
    lines.append(f"- Action items found: {len(actions)}")
    lines.append(f"- Planned tasks: {len(plan.tasks)}")
    lines.append("")

    lines.append("Extracted requirements")
    if deadlines:
        lines.append(f"- Deadlines: {', '.join(deadlines)}")
    if documents:
        lines.append(f"- Documents: {', '.join(documents)}")
    if actions:
        lines.append(f"- Actions: {', '.join(actions)}")
    if not (deadlines or documents or actions):
        lines.append("- No structured items were extracted from this message.")
        lines.append("- Recommended follow-up: collect the full request or a more detailed message.")
    lines.append("")

    lines.append("Execution status")
    if urgent:
        lines.append("- Urgent")
        for item in urgent[:4]:
            lines.append(f"  - {item}")
    if ready:
        lines.append("- Ready")
        for item in ready[:5]:
            lines.append(f"  - {item}")
    if blocked:
        lines.append("- Blocked")
        for item in blocked[:4]:
            lines.append(f"  - {item}")
    if not (urgent or ready or blocked):
        lines.append("- No operational tasks were generated.")
        lines.append("- This case is better treated as an incomplete request rather than a finalized workflow.")
    lines.append("")

    lines.append("Suggested handoff note")
    if plan.tasks:
        lines.append("- Use the recommended next action above as the first step.")
        lines.append("- Then work through ready items before revisiting blocked tasks.")
    else:
        lines.append("- Ask for the full administrative request before taking action.")

    return "\n".join(lines)


def generate_email_ready_reply(plan: Plan) -> str:
    if not plan.tasks:
        return (
            "Hello,\n\n"
            "Thank you for the message. I reviewed it, but I do not yet have enough concrete detail to act on specific items.\n"
            "If you send the full request, any deadlines, or the documents being requested, I can follow up more precisely.\n\n"
            "Best,\n"
            "Nesib"
        )

    urgent = [task.task for task in plan.tasks if task.status == "urgent"]
    ready = [task.task for task in plan.tasks if task.status == "ready"]

    lines = []
    lines.append("Hello,")
    lines.append("")
    lines.append("Thank you for the update. I reviewed the request and organized the next steps on my side.")

    if urgent:
        lines.append("")
        lines.append("I will prioritize the following first:")
        for task in urgent[:2]:
            lines.append(f"- {task}")

    if ready:
        lines.append("")
        lines.append("I can also move forward on:")
        for task in ready[:3]:
            lines.append(f"- {task}")

    lines.append("")
    lines.append("I will follow up once the requested items have been completed and uploaded.")
    lines.append("")
    lines.append("Best,")
    lines.append("Nesib")

    return "\n".join(lines)


def draft_response(plan: Plan) -> str:
    if not plan.tasks:
        return (
            "Hello,\n\n"
            "Thank you for the message. I reviewed it, but there is not enough specific information yet for me to act on concrete items.\n"
            "If you share the full request or any deadlines and requested documents, I can follow up more precisely.\n\n"
            "Best,\n"
            "Nesib"
        )

    urgent = [task for task in plan.tasks if task.status == "urgent"]
    ready = [task for task in plan.tasks if task.status == "ready"]

    lines = []
    lines.append("Hello,")
    lines.append("")
    lines.append("Thank you for the update. I reviewed the request and identified the main next steps on my side.")

    if urgent:
        lines.append("")
        lines.append("I will prioritize the following first:")
        for task in _top_tasks(urgent, limit=2):
            lines.append(f"- {task}")

    if ready:
        lines.append("")
        lines.append("I can also move forward on:")
        for task in _top_tasks(ready, limit=3):
            lines.append(f"- {task}")

    lines.append("")
    lines.append("I will follow up once the requested items have been submitted.")
    lines.append("")
    lines.append("Best,")
    lines.append("Nesib")

    return "\n".join(lines)


def draft_response_enhanced(plan: Plan) -> str:
    if not plan.tasks:
        return (
            "Hello,\n\n"
            "Thank you for the message. I reviewed it, but it does not yet include enough concrete detail for me to organize a full action plan.\n"
            "If you send the full request, any deadlines, or the specific documents being asked for, I can follow up more accurately.\n\n"
            "Best,\n"
            "Nesib"
        )

    urgent = [task for task in plan.tasks if task.status == "urgent"]
    ready = [task for task in plan.tasks if task.status == "ready"]
    blocked = [task for task in plan.tasks if task.status == "blocked"]

    lines = []
    lines.append("Hello,")
    lines.append("")
    lines.append("Thank you for the update. I reviewed the request and organized the next steps so I can work through them in order.")

    if urgent:
        lines.append("")
        lines.append("I will prioritize these first:")
        for task in _top_tasks(urgent, limit=3):
            lines.append(f"- {task}")

    if ready:
        lines.append("")
        lines.append("I can move forward immediately on:")
        for task in _top_tasks(ready, limit=4):
            lines.append(f"- {task}")

    if blocked:
        lines.append("")
        lines.append("A few items depend on earlier steps being completed first:")
        for task in _top_tasks(blocked, limit=3):
            lines.append(f"- {task}")

    lines.append("")
    lines.append("I will follow up once everything has been submitted, or sooner if anything needs clarification.")
    lines.append("")
    lines.append("Best,")
    lines.append("Nesib")

    return "\n".join(lines)


def draft_response_with_mode(plan: Plan, enhanced: bool = False) -> str:
    if enhanced:
        return draft_response_enhanced(plan)
    return draft_response(plan)
