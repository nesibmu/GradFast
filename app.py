import streamlit as st

from visaflow.config import SAMPLES_DIR
from visaflow.ingestion.loaders import load_document
from visaflow.extraction.extractors import extract_information
from visaflow.planning.planner import build_task_plan
from visaflow.drafting.drafter import draft_response_with_mode, generate_next_step_summary


DEMO_PRESETS = {
    "Housing follow-up": {
        "text": """Subject: Additional documents needed for spring housing approval

Hello Nesib,

To complete your housing review, please submit your updated housing contract request and a recent bank statement by May 28, 2026. You should also upload a copy of your passport and current I-20 through the student portal.

Please confirm once the materials have been uploaded. If you need an extension, respond to this message as soon as possible.

Best,
Housing Assignments""",
        "description": "Shows deadline extraction, document requests, portal upload actions, and follow-up handling.",
    },
    "Financial aid review": {
        "text": """Subject: Missing documents for financial aid review

Hello Nesib,

We reviewed your file and still need a signed statement of support and your most recent bank statement.

Please upload both documents by June 3, 2026. If you are unable to meet this deadline, reply to this email as soon as possible.

Best,
Financial Aid Office""",
        "description": "Shows document extraction from sentence-style requests and deadline-driven prioritization.",
    },
    "Immigration update": {
        "text": """Subject: Missing immigration documents

Hello,

To complete your record, please upload a copy of your passport and your current I-20 by June 12, 2026 through the student portal.

Please confirm once the materials have been uploaded.

Best,
International Student Office""",
        "description": "Shows immigration-related document handling and action-item extraction.",
    },
    "Mixed admin case": {
        "text": """Subject: Follow-up on housing and immigration documents

Hello Nesib,

To complete your file, please upload your signed housing agreement, a recent bank statement, a copy of your passport, and your current I-20 by June 15, 2026 through the student portal.

Please confirm once the documents have been uploaded. If you expect any delay, reply to this message as soon as possible.

Best,
Student Services""",
        "description": "Shows a mixed workflow with housing, financial, and immigration-related tasks in one case.",
    },
}


def run_pipeline_from_text(text: str):
    extracted = extract_information(text)
    plan = build_task_plan(extracted)
    summary = generate_next_step_summary(plan)
    baseline_draft = draft_response_with_mode(plan, enhanced=False)
    enhanced_draft = draft_response_with_mode(plan, enhanced=True)
    return extracted, plan, summary, baseline_draft, enhanced_draft


def priority_color(priority: str) -> str:
    if priority == "high":
        return "#ef4444"
    if priority == "medium":
        return "#f59e0b"
    return "#9ca3af"


def status_badge(status: str) -> str:
    colors = {
        "urgent": ("#fee2e2", "#991b1b"),
        "ready": ("#dcfce7", "#166534"),
        "blocked": ("#e5e7eb", "#374151"),
    }
    bg, fg = colors.get(status, ("#f3f4f6", "#111827"))
    return f"<span style='background:{bg};color:{fg};padding:4px 8px;border-radius:999px;font-size:12px;font-weight:600;'>{status}</span>"


def confidence_label(score: float) -> str:
    if score >= 0.9:
        return "high"
    if score >= 0.75:
        return "medium"
    return "low"


def render_extraction_card(title: str, items, confidence_map, evidence_map):
    st.markdown(f"### {title}")
    if not items:
        st.caption(f"No {title.lower()} found.")
        return

    for item in items:
        score = confidence_map.get(item, 0.0)
        label = confidence_label(score)
        evidence = evidence_map.get(item, "")

        st.markdown(
            f"""
<div style="border:1px solid #e5e7eb;border-radius:14px;padding:14px 16px;margin-bottom:10px;background:white;">
  <div style="display:flex;justify-content:space-between;align-items:center;gap:12px;">
    <div style="font-weight:600;font-size:15px;">{item}</div>
    <div style="font-size:12px;padding:4px 8px;border-radius:999px;background:#f3f4f6;">
      confidence: {label} ({score:.2f})
    </div>
  </div>
  <div style="margin-top:8px;font-size:13px;color:#6b7280;">
    {evidence if evidence else "No supporting snippet found."}
  </div>
</div>
""",
            unsafe_allow_html=True,
        )


def render_task_card(task):
    color = priority_color(task.priority)
    depends = ""
    if task.depends_on:
        depends = f"<div style='margin-top:8px;font-size:12px;color:#6b7280;'>Depends on: {', '.join(task.depends_on)}</div>"

    st.markdown(
        f"""
<div style="border-left:6px solid {color};border-radius:12px;padding:14px 16px;margin-bottom:12px;background:#ffffff;border:1px solid #e5e7eb;">
  <div style="display:flex;justify-content:space-between;align-items:center;gap:12px;">
    <div style="font-weight:600;font-size:15px;">{task.task}</div>
    <div>{status_badge(task.status)}</div>
  </div>
  <div style="margin-top:8px;font-size:12px;color:#6b7280;">
    workflow: {task.workflow_type} • source: {task.source} • priority: {task.priority}
  </div>
  {depends}
</div>
""",
        unsafe_allow_html=True,
    )


st.set_page_config(page_title="VisaFlow", layout="wide")

st.markdown(
    """
<style>
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    max-width: 1200px;
}
div[data-testid="stMetric"] {
    background: #ffffff;
    border: 1px solid #e5e7eb;
    padding: 12px;
    border-radius: 14px;
}
</style>
""",
    unsafe_allow_html=True,
)

st.title("VisaFlow")
st.caption("AI operations agent for international-student bureaucracy")

st.markdown(
    """
VisaFlow turns administrative communication into a clearer workflow:
- extract deadlines, requested documents, and action items
- show supporting evidence
- build a prioritized task plan
- generate draft responses that can be edited and downloaded
"""
)

sample_files = sorted([p.name for p in SAMPLES_DIR.glob("*.txt")])

with st.sidebar:
    st.header("Demo Controls")
    input_mode = st.radio(
        "Input mode",
        ["Demo preset", "Sample file", "Paste text", "Upload file"],
        index=0,
    )
    show_comparison = st.checkbox("Show baseline vs enhanced draft", value=True)

    selected_preset = None
    selected_file = None
    pasted_text = ""
    uploaded_file = None

    if input_mode == "Demo preset":
        selected_preset = st.selectbox("Choose a preset", list(DEMO_PRESETS.keys()), index=0)
        st.caption(DEMO_PRESETS[selected_preset]["description"])
    elif input_mode == "Sample file":
        selected_file = st.selectbox("Choose a sample file", sample_files)
    elif input_mode == "Paste text":
        pasted_text = st.text_area(
            "Paste email or document text",
            height=220,
            placeholder="Paste an administrative email or document here...",
        )
    else:
        uploaded_file = st.file_uploader("Upload a .txt file", type=["txt"])

    run_pipeline = st.button("Run pipeline", use_container_width=True)

if run_pipeline:
    source_text = ""

    if input_mode == "Demo preset":
        source_text = DEMO_PRESETS[selected_preset]["text"]
    elif input_mode == "Sample file":
        document = load_document(SAMPLES_DIR / selected_file)
        source_text = document.text
    elif input_mode == "Paste text":
        source_text = pasted_text.strip()
    else:
        if uploaded_file is not None:
            source_text = uploaded_file.read().decode("utf-8").strip()

    if not source_text:
        st.warning("Please choose a preset, enter text, or upload a file before running the pipeline.")
    else:
        extracted, plan, summary, baseline_draft, enhanced_draft = run_pipeline_from_text(source_text)

        deadlines = extracted.get("deadlines", [])
        documents = extracted.get("requested_documents", [])
        actions = extracted.get("action_items", [])
        evidence = extracted.get("evidence", {})
        confidence = extracted.get("confidence", {})

        urgent_count = len([task for task in plan.tasks if task.status == "urgent"])
        ready_count = len([task for task in plan.tasks if task.status == "ready"])
        blocked_count = len([task for task in plan.tasks if task.status == "blocked"])
        workflow_count = len(set(task.workflow_type for task in plan.tasks))

        st.subheader("Overview")
        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("Deadlines", len(deadlines))
        m2.metric("Documents", len(documents))
        m3.metric("Actions", len(actions))
        m4.metric("Urgent / Ready / Blocked", f"{urgent_count} / {ready_count} / {blocked_count}")
        m5.metric("Workflows", workflow_count)

        st.divider()

        left, right = st.columns([1.15, 0.85])
        with left:
            st.subheader("Source Text")
            st.text_area("Input", source_text, height=260)
        with right:
            st.subheader("Operational Summary")
            st.text_area("Summary", summary, height=260)

        st.divider()

        c1, c2, c3 = st.columns(3)
        with c1:
            render_extraction_card(
                "Deadlines",
                deadlines,
                confidence.get("deadlines", {}),
                evidence.get("deadlines", {}),
            )
        with c2:
            render_extraction_card(
                "Requested Documents",
                documents,
                confidence.get("requested_documents", {}),
                evidence.get("requested_documents", {}),
            )
        with c3:
            render_extraction_card(
                "Action Items",
                actions,
                confidence.get("action_items", {}),
                evidence.get("action_items", {}),
            )

        st.divider()

        st.subheader("Task Plan")

        workflow_options = ["all"] + sorted({task.workflow_type for task in plan.tasks})
        priority_options = ["all", "high", "medium", "low"]
        status_options = ["all", "urgent", "ready", "blocked"]

        f1, f2, f3 = st.columns(3)
        with f1:
            selected_workflow = st.selectbox("Filter by workflow", workflow_options)
        with f2:
            selected_priority = st.selectbox("Filter by priority", priority_options)
        with f3:
            selected_status = st.selectbox("Filter by status", status_options)

        filtered_tasks = []
        for task in plan.tasks:
            workflow_ok = selected_workflow == "all" or task.workflow_type == selected_workflow
            priority_ok = selected_priority == "all" or task.priority == selected_priority
            status_ok = selected_status == "all" or task.status == selected_status
            if workflow_ok and priority_ok and status_ok:
                filtered_tasks.append(task)

        if filtered_tasks:
            for task in filtered_tasks:
                render_task_card(task)
        else:
            st.caption("No tasks match the selected filters.")

        st.divider()
        st.subheader("Draft Response")

        if show_comparison:
            d1, d2 = st.columns(2)
            with d1:
                st.markdown("**Baseline Draft**")
                baseline_editable = st.text_area("Baseline", baseline_draft, height=260)
                st.download_button(
                    label="Download baseline draft",
                    data=baseline_editable,
                    file_name="visaflow_baseline_draft.txt",
                    mime="text/plain",
                    key="download_baseline",
                    use_container_width=True,
                )
            with d2:
                st.markdown("**Enhanced Draft**")
                enhanced_editable = st.text_area("Enhanced", enhanced_draft, height=260)
                st.download_button(
                    label="Download enhanced draft",
                    data=enhanced_editable,
                    file_name="visaflow_enhanced_draft.txt",
                    mime="text/plain",
                    key="download_enhanced",
                    use_container_width=True,
                )
        else:
            editable_draft = st.text_area("Editable draft", enhanced_draft, height=260)
            st.download_button(
                label="Download draft as .txt",
                data=editable_draft,
                file_name="visaflow_draft.txt",
                mime="text/plain",
                use_container_width=True,
            )
else:
    st.info("Choose a preset, sample file, pasted text, or uploaded file, then click Run pipeline.")
