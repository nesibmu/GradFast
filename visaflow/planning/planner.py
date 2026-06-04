from datetime import datetime
from visaflow.schemas import Plan, PlannedTask


PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}
SOURCE_ORDER = {"deadline": 0, "requested_document": 1, "action_item": 2}
WORKFLOW_ORDER = {"housing": 0, "financial_aid": 1, "immigration": 2, "general": 3}


def workflow_term_scores(text: str):
    lowered = text.lower()

    housing_terms = [
        "housing", "room assignment", "housing agreement", "housing contract",
        "contract request", "lease", "residential", "assignment", "room"
    ]
    finance_terms = [
        "financial aid", "bank statement", "statement of support",
        "funding", "payment", "tuition", "billing", "finance", "support"
    ]
    immigration_terms = [
        "passport", "i-20", "visa", "immigration", "sevis", "travel signature"
    ]

    return {
        "housing": sum(term in lowered for term in housing_terms),
        "financial_aid": sum(term in lowered for term in finance_terms),
        "immigration": sum(term in lowered for term in immigration_terms),
    }


def infer_workflow_type(text: str) -> str:
    scores = workflow_term_scores(text)
    best_workflow = max(scores, key=scores.get)
    if scores[best_workflow] == 0:
        return "general"
    return best_workflow


def infer_workflow_type_with_context(text: str, document_tasks=None) -> str:
    direct = infer_workflow_type(text)
    if direct != "general":
        return direct

    lowered = text.lower()

    generic_admin_phrases = [
        "student portal",
        "complete your file",
        "finish the review",
        "confirm completion",
        "confirm once",
        "uploaded",
        "materials",
        "documents have been uploaded",
        "review",
        "file",
    ]

    if any(phrase in lowered for phrase in generic_admin_phrases) and document_tasks:
        counts = {"housing": 0, "financial_aid": 0, "immigration": 0}
        for task in document_tasks:
            if task.workflow_type in counts:
                counts[task.workflow_type] += 1

        best = max(counts, key=counts.get)
        if counts[best] > 0:
            return best

    return "general"


def infer_priority(task_text: str, source: str) -> str:
    lowered = task_text.lower()

    if source == "deadline":
        return "high"

    if source == "requested_document":
        if any(word in lowered for word in ["passport", "bank statement", "i-20", "agreement", "enrollment"]):
            return "high"
        return "medium"

    if source == "action_item":
        if any(word in lowered for word in ["as soon as possible", "respond", "reply", "confirm"]):
            return "medium"
        if any(word in lowered for word in ["submit", "upload", "portal"]):
            return "high"
        return "low"

    return "medium"


def parse_deadline(date_text: str):
    formats = ["%B %d, %Y", "%B %d"]
    for fmt in formats:
        try:
            dt = datetime.strptime(date_text, fmt)
            if fmt == "%B %d":
                dt = dt.replace(year=datetime.now().year)
            return dt
        except ValueError:
            continue
    return None


def is_due_soon(date_text: str, days_threshold: int = 7) -> bool:
    dt = parse_deadline(date_text)
    if dt is None:
        return False
    delta = (dt.date() - datetime.now().date()).days
    return 0 <= delta <= days_threshold


def sort_deadlines(deadlines):
    def deadline_key(date_text):
        parsed = parse_deadline(date_text)
        if parsed is None:
            return datetime.max
        return parsed

    return sorted(deadlines, key=deadline_key)


def infer_status(source: str, priority: str, depends_on):
    if source == "deadline":
        return "urgent"
    if depends_on:
        return "blocked"
    if priority == "high":
        return "ready"
    return "ready"


def summarize_dependencies(depends_on):
    if not depends_on:
        return ""

    if len(depends_on) == 1:
        return f"Waiting on: {depends_on[0]}"
    if len(depends_on) == 2:
        return f"Waiting on: {depends_on[0]} and {depends_on[1]}"
    return f"Waiting on {len(depends_on)} earlier steps, including {depends_on[0]}"


def compute_urgency_score(task_text: str, source: str, status: str, depends_on):
    lowered = task_text.lower()
    score = 0

    if status == "urgent":
        score += 100
    elif status == "ready":
        score += 60
    elif status == "blocked":
        score += 20

    if "[due soon]" in lowered:
        score += 40

    if source == "deadline":
        score += 25

    if any(term in lowered for term in ["passport", "i-20", "bank statement", "statement of support"]):
        score += 15

    if any(term in lowered for term in ["reply", "respond", "confirm", "as soon as possible"]):
        score += 10

    if source == "action_item" and ("upload" in lowered or "submit" in lowered):
        score += 8

    if depends_on:
        score -= min(10, len(depends_on))

    return score


def deduplicate_tasks(tasks):
    seen = set()
    unique_tasks = []

    for task in tasks:
        key = (task.task.lower(), task.source, task.workflow_type)
        if key not in seen:
            seen.add(key)
            unique_tasks.append(task)

    return unique_tasks


def sort_tasks(tasks):
    status_order = {"urgent": 0, "ready": 1, "blocked": 2}
    return sorted(
        tasks,
        key=lambda task: (
            status_order.get(task.status, 99),
            -task.urgency_score,
            WORKFLOW_ORDER.get(task.workflow_type, 99),
            PRIORITY_ORDER.get(task.priority, 99),
            SOURCE_ORDER.get(task.source, 99),
            task.task.lower(),
        ),
    )


def build_upload_packet_task(document_tasks):
    if not document_tasks:
        return None

    workflow_counts = {"housing": 0, "financial_aid": 0, "immigration": 0}
    for task in document_tasks:
        if task.workflow_type in workflow_counts:
            workflow_counts[task.workflow_type] += 1

    dominant = max(workflow_counts, key=workflow_counts.get)
    workflow_type = dominant if workflow_counts[dominant] > 0 else "general"

    depends_on = [task.task for task in document_tasks]
    status = "blocked"
    task_text = "Compile and upload requested document packet"
    return PlannedTask(
        task=task_text,
        priority="high",
        source="action_item",
        workflow_type=workflow_type,
        status=status,
        depends_on=depends_on,
        blocking_reason=summarize_dependencies(depends_on),
        urgency_score=compute_urgency_score(task_text, "action_item", status, depends_on),
    )


def infer_dependencies(action_text: str, document_tasks, upload_packet_task):
    lowered = action_text.lower()

    if "confirm" in lowered or "reply" in lowered or "respond" in lowered:
        deps = []
        if upload_packet_task is not None:
            deps.append(upload_packet_task.task)
        deps.extend(task.task for task in document_tasks)
        return deps

    if "upload" in lowered or "portal" in lowered or "submit" in lowered:
        return [task.task for task in document_tasks]

    matching_dependencies = []
    for task in document_tasks:
        if task.workflow_type != "general" and task.workflow_type in lowered:
            matching_dependencies.append(task.task)

    return matching_dependencies


def build_task_plan(extracted: dict) -> Plan:
    tasks = []
    document_tasks = []

    ordered_deadlines = sort_deadlines(extracted.get("deadlines", []))

    for idx, deadline in enumerate(ordered_deadlines):
        label = f"Track deadline: {deadline}"
        if idx == 0 and len(ordered_deadlines) > 1:
            label += " [earliest]"
        if is_due_soon(deadline):
            label += " [due soon]"
        priority = infer_priority(label, "deadline")
        status = infer_status("deadline", priority, [])
        tasks.append(
            PlannedTask(
                task=label,
                priority=priority,
                source="deadline",
                workflow_type="general",
                status=status,
                blocking_reason="",
                urgency_score=compute_urgency_score(label, "deadline", status, []),
            )
        )

    for document in extracted.get("requested_documents", []):
        task_text = f"Prepare document: {document}"
        workflow_type = infer_workflow_type(document)
        priority = infer_priority(task_text, "requested_document")
        status = infer_status("requested_document", priority, [])
        planned = PlannedTask(
            task=task_text,
            priority=priority,
            source="requested_document",
            workflow_type=workflow_type,
            status=status,
            blocking_reason="",
            urgency_score=compute_urgency_score(task_text, "requested_document", status, []),
        )
        tasks.append(planned)
        document_tasks.append(planned)

    upload_packet_task = build_upload_packet_task(document_tasks)
    if upload_packet_task is not None:
        tasks.append(upload_packet_task)

    for action in extracted.get("action_items", []):
        task_text = f"Complete action: {action}"
        workflow_type = infer_workflow_type_with_context(action, document_tasks=document_tasks)
        depends_on = infer_dependencies(action, document_tasks, upload_packet_task)
        priority = infer_priority(task_text, "action_item")
        status = infer_status("action_item", priority, depends_on)
        tasks.append(
            PlannedTask(
                task=task_text,
                priority=priority,
                source="action_item",
                workflow_type=workflow_type,
                depends_on=depends_on,
                status=status,
                blocking_reason=summarize_dependencies(depends_on),
                urgency_score=compute_urgency_score(task_text, "action_item", status, depends_on),
            )
        )

    tasks = deduplicate_tasks(tasks)
    tasks = sort_tasks(tasks)

    return Plan(tasks=tasks)
