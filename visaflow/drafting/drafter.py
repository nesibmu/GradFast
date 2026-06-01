from visaflow.schemas import Plan


def draft_response(plan: Plan) -> str:
    if not plan.tasks:
        return "No immediate action items were identified."

    high_priority = [task for task in plan.tasks if task.priority == "high"]
    medium_priority = [task for task in plan.tasks if task.priority == "medium"]
    low_priority = [task for task in plan.tasks if task.priority == "low"]

    lines = []
    lines.append("Suggested next steps")
    lines.append("")

    if high_priority:
        lines.append("Urgent:")
        for task in high_priority:
            lines.append(f"- {task.task}")
        lines.append("")

    if medium_priority:
        lines.append("Important follow-up:")
        for task in medium_priority:
            lines.append(f"- {task.task}")
        lines.append("")

    if low_priority:
        lines.append("Lower-priority items:")
        for task in low_priority:
            lines.append(f"- {task.task}")
        lines.append("")

    lines.append("Draft reply:")
    lines.append("Hello,")
    lines.append("")
    lines.append("Thank you for the update. I will work on the requested items and follow up once everything has been submitted.")
    lines.append("")
    lines.append("Best,")
    lines.append("Nesib")

    return "\n".join(lines)
