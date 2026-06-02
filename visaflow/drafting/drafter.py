from visaflow.schemas import Plan


def _top_tasks(tasks, limit=4):
    return [task.task for task in tasks[:limit]]


def generate_recommended_next_action(plan: Plan) -> str:
    if not plan.tasks:
        return "No clear next action was identified."

    urgent = [task for task in plan.tasks if task.status == "urgent"]
    ready = [task for task in plan.tasks if task.status == "ready"]
    blocked = [task for task in plan.tasks if task.status == "blocked"]

    if urgent:
        return f"Recommended next action: {urgent[0].task}"
    if ready:
        return f"Recommended next action: {ready[0].task}"
    if blocked:
        return f"Recommended next action: unblock {blocked[0].task}"
    return "No clear next action was identified."


def generate_next_step_summary(plan: Plan) -> str:
    if not plan.tasks:
        return "No immediate action items were identified."

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
        return "No checklist items available."

    lines = []
    lines.append("Action checklist")
    lines.append("")

    for task in plan.tasks:
        label = task.status.upper()
        lines.append(f"[ ] {task.task}  |  {label}")

    return "\n".join(lines)


def draft_response(plan: Plan) -> str:
    if not plan.tasks:
        return "No immediate action items were identified."

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
        return "Hello,\n\nThank you for the message. I do not see any immediate action items right now, but I will review everything again and follow up if needed.\n\nBest,\nNesib"

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
