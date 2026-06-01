from visaflow.schemas import Plan


def render_result(source_text: str, extracted: dict, plan: Plan, response: str) -> str:
    lines = []

    lines.append("=== Source ===")
    lines.append(source_text)
    lines.append("")

    lines.append("=== Extracted Information ===")
    lines.append(f"Deadlines: {extracted.get('deadlines', [])}")
    lines.append(f"Requested documents: {extracted.get('requested_documents', [])}")
    lines.append(f"Action items: {extracted.get('action_items', [])}")
    lines.append("")

    lines.append("=== Plan ===")
    if plan.tasks:
        for task in plan.tasks:
            lines.append(f"- {task.task} [{task.priority}]")
    else:
        lines.append("No tasks generated.")
    lines.append("")

    lines.append("=== Draft Response ===")
    lines.append(response)

    return "\n".join(lines)
