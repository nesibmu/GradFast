from visaflow.schemas import Plan
from visaflow.drafting.drafter import generate_next_step_summary


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

    evidence = extracted.get("evidence", {})
    if evidence:
        lines.append("=== Evidence ===")
        for category in ["deadlines", "requested_documents", "action_items"]:
            category_evidence = evidence.get(category, {})
            if category_evidence:
                lines.append(f"{category}:")
                for item, snippet in category_evidence.items():
                    lines.append(f"- {item} -> {snippet}")
        lines.append("")

    lines.append("=== Plan ===")
    if plan.tasks:
        current_workflow = None
        for task in plan.tasks:
            if task.workflow_type != current_workflow:
                current_workflow = task.workflow_type
                lines.append(f"[{current_workflow}]")
            suffix = ""
            if task.depends_on:
                suffix = f" -> depends on: {task.depends_on}"
            lines.append(f"- {task.task} [{task.priority}]{suffix}")
    else:
        lines.append("No tasks generated.")
    lines.append("")

    lines.append("=== Next-Step Summary ===")
    lines.append(generate_next_step_summary(plan))
    lines.append("")

    lines.append("=== Draft Response ===")
    lines.append(response)

    return "\n".join(lines)
