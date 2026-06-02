import streamlit as st

from visaflow.config import SAMPLES_DIR
from visaflow.ingestion.loaders import load_document
from visaflow.extraction.extractors import extract_information
from visaflow.planning.planner import build_task_plan
from visaflow.drafting.drafter import (
    draft_response_with_mode,
    generate_next_step_summary,
    generate_action_checklist,
)


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
    checklist = generate_action_checklist(plan)
    baseline_draft = draft_response_with_mode(plan, enhanced=False)
    enhanced_draft = draft_response_with_mode(plan, enhanced=True)
    return {
        "source_text": text,
        "extracted": extracted,
        "plan": plan,
        "summary": summary,
        "checklist": checklist,
        "baseline_draft": baseline_draft,
        "enhanced_draft": enhanced_draft,
    }


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


def confidence_chip(score: float) -> str:
    label = confidence_label(score)
    colors = {
        "high": ("#dcfce7", "#166534"),
        "medium": ("#fef3c7", "#92400e"),
        "low": ("#fee2e2", "#991b1b"),
    }
    bg, fg = colors[label]
    return f"<span style='background:{bg};color:{fg};padding:4px 8px;border-radius:999px;font-size:12px;font-weight:600;'>{label} ({score:.2f})</span>"


def render_compact_findings(title: str, items, confidence_map):
    st.markdown(f"#### {title}")
    if not items:
        st.caption("None found.")
        return

    for item in items:
        score = confidence_map.get(item, 0.0)
        st.markdown(
            f"""
<div style="border:1px solid #e5e7eb;border-radius:12px;padding:12px 14px;margin-bottom:8px;background:white;">
  <div style="display:flex;justify-content:space-between;align-items:center;gap:10px;">
    <div style="font-weight:600;font-size:14px;">{item}</div>
    <div>{confidence_chip(score)}</div>
  </div>
</div>
""",
            unsafe_allow_html=True,
        )


def render_evidence_panel(title: str, items, evidence_map):
    st.markdown(f"#### {title}")
    if not items:
        st.caption("No evidence to show.")
        return

    for item in items:
        snippet = evidence_map.get(item, "No supporting snippet found.")
        st.markdown(
            f"""
<div style="border:1px dashed #d1d5db;border-radius:12px;padding:12px 14px;margin-bottom:8px;background:#fafafa;">
  <div style="font-size:13px;font-weight:600;margin-bottom:6px;">{item}</div>
  <div style="font-size:13px;color:#6b7280;">{snippet}</div>
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
    padding-top: 1.5rem;
    padding-bottom: 2rem;
    max-width: 1250px;
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

if "results" not in st.session_state:
    st.session_state.results = None

sample_files = sorted([p.name for p in SAMPLES_DIR.glob("*.txt")])

with st.sidebar:
    st.header("Demo Controls")
    presenter_mode = st.checkbox("Presenter mode", value=False)
    input_mode = st.radio(
        "Input mode",
        ["Demo preset", "Sample file", "Paste text", "Upload file"],
        index=0,
    )

    selected_preset = None
    selected_file = None
    pasted_text = ""
    uploaded_file = None

    if input_mode == "Demo preset":
        selected_preset = st.selectbox("Choose a preset", list(DEMO_PRESETS.keys()), index=0)
        if not presenter_mode:
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
    clear_results = st.button("Clear current results", use_container_width=True)

hero_left, hero_right = st.columns([1.35, 0.9])

with hero_left:
    st.markdown("# VisaFlow")
    st.markdown("**AI operations agent for international-student bureaucracy**")
    if presenter_mode:
        st.markdown(
            """
A local demo tool for turning messy administrative requests into:
- extracted requirements
- prioritized tasks
- usable response drafts
"""
        )
    else:
        st.markdown(
            """
VisaFlow helps turn administrative communication into a clearer workflow:
- extract deadlines, requested documents, and action items
- surface evidence and confidence
- build a prioritized task plan
- generate editable response outputs
"""
        )

with hero_right:
    current_mode_label = input_mode
    current_case_label = selected_preset if input_mode == "Demo preset" and selected_preset else "Custom input"
    st.markdown(
        f"""
<div style="border:1px solid #e5e7eb;border-radius:16px;padding:16px;background:#ffffff;">
  <div style="font-size:12px;color:#6b7280;margin-bottom:8px;">Current demo state</div>
  <div style="font-size:18px;font-weight:700;margin-bottom:8px;">{current_case_label}</div>
  <div style="font-size:13px;color:#4b5563;">Mode: {current_mode_label}</div>
  <div style="font-size:13px;color:#4b5563;">Presenter mode: {"on" if presenter_mode else "off"}</div>
</div>
""",
        unsafe_allow_html=True,
    )

st.divider()

st.subheader("Quick Demo Launch")
q1, q2, q3, q4 = st.columns(4)
preset_names = list(DEMO_PRESETS.keys())
quick_clicked = None

if q1.button(preset_names[0], use_container_width=True):
    quick_clicked = preset_names[0]
if q2.button(preset_names[1], use_container_width=True):
    quick_clicked = preset_names[1]
if q3.button(preset_names[2], use_container_width=True):
    quick_clicked = preset_names[2]
if q4.button(preset_names[3], use_container_width=True):
    quick_clicked = preset_names[3]

if clear_results:
    st.session_state.results = None

if quick_clicked is not None:
    st.session_state.results = run_pipeline_from_text(DEMO_PRESETS[quick_clicked]["text"])

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
        st.session_state.results = run_pipeline_from_text(source_text)

results = st.session_state.results

if results is not None:
    source_text = results["source_text"]
    extracted = results["extracted"]
    plan = results["plan"]
    summary = results["summary"]
    checklist = results["checklist"]
    baseline_draft = results["baseline_draft"]
    enhanced_draft = results["enhanced_draft"]

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

    st.subheader("Extraction Dashboard")

    d1, d2, d3 = st.columns(3)
    with d1:
        render_compact_findings("Deadlines", deadlines, confidence.get("deadlines", {}))
    with d2:
        render_compact_findings("Requested Documents", documents, confidence.get("requested_documents", {}))
    with d3:
        render_compact_findings("Action Items", actions, confidence.get("action_items", {}))

    if not presenter_mode:
        st.markdown("#### Evidence by Category")
        e1, e2, e3 = st.columns(3)
        with e1:
            render_evidence_panel("Deadline Evidence", deadlines, evidence.get("deadlines", {}))
        with e2:
            render_evidence_panel("Document Evidence", documents, evidence.get("requested_documents", {}))
        with e3:
            render_evidence_panel("Action Evidence", actions, evidence.get("action_items", {}))

    st.divider()

    st.subheader("Task Plan")

    if presenter_mode:
        filtered_tasks = plan.tasks
    else:
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

    if not presenter_mode:
        st.divider()
        with st.expander("Trace View", expanded=False):
            st.markdown("### Source to Output Mapping")
            for category in ["deadlines", "requested_documents", "action_items"]:
                items = extracted.get(category, [])
                if items:
                    st.markdown(f"**{category.replace('_', ' ').title()}**")
                    for item in items:
                        matched_tasks = [task.task for task in plan.tasks if item.lower() in task.task.lower()]
                        snippet = evidence.get(category, {}).get(item, "No snippet found.")
                        conf = confidence.get(category, {}).get(item, 0.0)
                        st.markdown(
                            f"""
<div style="border:1px solid #e5e7eb;border-radius:12px;padding:12px;margin-bottom:10px;background:#fafafa;">
  <div><strong>Item:</strong> {item}</div>
  <div style="margin-top:6px;"><strong>Confidence:</strong> {conf:.2f}</div>
  <div style="margin-top:6px;"><strong>Evidence:</strong> {snippet}</div>
  <div style="margin-top:6px;"><strong>Mapped tasks:</strong> {matched_tasks if matched_tasks else 'None'}</div>
</div>
""",
                            unsafe_allow_html=True,
                        )

    st.divider()
    st.subheader("Response Workspace")

    if presenter_mode:
        tab1, tab2 = st.tabs(["Enhanced Draft", "Checklist"])
        with tab1:
            enhanced_editable = st.text_area("Enhanced Draft", enhanced_draft, height=320)
            st.download_button(
                label="Download enhanced draft",
                data=enhanced_editable,
                file_name="visaflow_enhanced_draft.txt",
                mime="text/plain",
                use_container_width=True,
                key="download_enhanced_presenter",
            )
        with tab2:
            checklist_text = st.text_area("Action Checklist", checklist, height=320)
            st.download_button(
                label="Download checklist",
                data=checklist_text,
                file_name="visaflow_checklist.txt",
                mime="text/plain",
                use_container_width=True,
                key="download_checklist_presenter",
            )
    else:
        tab1, tab2, tab3, tab4 = st.tabs(["Summary", "Baseline Draft", "Enhanced Draft", "Checklist"])

        with tab1:
            st.text_area("Summary view", summary, height=280)
            st.download_button(
                label="Download summary",
                data=summary,
                file_name="visaflow_summary.txt",
                mime="text/plain",
                use_container_width=True,
                key="download_summary",
            )

        with tab2:
            baseline_editable = st.text_area("Baseline Draft", baseline_draft, height=320)
            st.download_button(
                label="Download baseline draft",
                data=baseline_editable,
                file_name="visaflow_baseline_draft.txt",
                mime="text/plain",
                use_container_width=True,
                key="download_baseline",
            )

        with tab3:
            enhanced_editable = st.text_area("Enhanced Draft", enhanced_draft, height=320)
            st.download_button(
                label="Download enhanced draft",
                data=enhanced_editable,
                file_name="visaflow_enhanced_draft.txt",
                mime="text/plain",
                use_container_width=True,
                key="download_enhanced",
            )

        with tab4:
            checklist_text = st.text_area("Action Checklist", checklist, height=320)
            st.download_button(
                label="Download checklist",
                data=checklist_text,
                file_name="visaflow_checklist.txt",
                mime="text/plain",
                use_container_width=True,
                key="download_checklist",
            )
else:
    st.info("Choose a preset, sample file, pasted text, or uploaded file, then click Run pipeline, or use a Quick Demo Launch button.")
