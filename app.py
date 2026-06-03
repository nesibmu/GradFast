import streamlit as st

from visaflow.config import SAMPLES_DIR
from visaflow.ingestion.loaders import load_document
from visaflow.extraction.extractors import extract_information
from visaflow.planning.planner import build_task_plan
import visaflow.drafting.drafter as drafter


APP_TITLE = "VisaFlow"
APP_SUBTITLE = "AI-assisted workflow organizer for administrative messages"

DEMO_PRESETS = {
    "Mixed admin case": {
        "text": """Subject: Follow-up on housing and immigration documents

Hello Nesib,

To complete your file, please upload your signed housing agreement, a recent bank statement, a copy of your passport, and your current I-20 by June 15, 2026 through the student portal.

Please confirm once the documents have been uploaded. If you expect any delay, reply to this message as soon as possible.

Best,
Student Services""",
        "note": "Best default demo. Shows multiple requested documents, a deadline, and follow-up actions.",
    },
    "Escalated admin case": {
        "text": """Subject: Urgent follow-up on housing, financial aid, and immigration items

Hello Nesib,

We are still missing your signed housing agreement, updated bank statement, current passport copy, current I-20, and statement of support.

Please upload all materials through the student portal by June 10, 2026. You should also reply to this email by June 8, 2026 if you expect any delay. Once everything has been uploaded, please confirm completion so we can finish the review.

Best,
Student Services and Financial Support""",
        "note": "Dense case. Shows multiple deadlines and stronger urgency.",
    },
    "Housing follow-up": {
        "text": """Subject: Additional documents needed for spring housing approval

Hello Nesib,

To complete your housing review, please submit your updated housing contract request and a recent bank statement by May 28, 2026. You should also upload a copy of your passport and current I-20 through the student portal.

Please confirm once the materials have been uploaded. If you need an extension, respond to this message as soon as possible.

Best,
Housing Assignments""",
        "note": "Simple case for a clean walkthrough.",
    },
    "Financial aid review": {
        "text": """Subject: Missing documents for financial aid review

Hello Nesib,

We reviewed your file and still need a signed statement of support and your most recent bank statement.

Please upload both documents by June 3, 2026. If you are unable to meet this deadline, reply to this email as soon as possible.

Best,
Financial Aid Office""",
        "note": "Good for showing sentence-based extraction.",
    },
    "Immigration update": {
        "text": """Subject: Missing immigration documents

Hello,

To complete your record, please upload a copy of your passport and your current I-20 by June 12, 2026 through the student portal.

Please confirm once the materials have been uploaded.

Best,
International Student Office""",
        "note": "Good for immigration workflow tagging.",
    },
    "Weak noisy case": {
        "text": """Subject: quick follow up

hi, just checking in on the file. send what you can soon and let us know if anything changed.

thanks""",
        "note": "Best robustness case. Shows fallback behavior on incomplete input.",
    },
}


def safe_call(name, *args, fallback=""):
    fn = getattr(drafter, name, None)
    if fn is None:
        return fallback
    try:
        return fn(*args)
    except Exception:
        return fallback


def run_pipeline_from_text(text: str):
    extracted = extract_information(text)
    plan = build_task_plan(extracted)

    summary = safe_call("generate_next_step_summary", plan, fallback="No summary available.")
    short_summary = safe_call("generate_short_summary", plan, extracted, fallback="Short summary unavailable.")
    recommended_next_action = safe_call("generate_recommended_next_action", plan, fallback="No recommended next action available.")
    checklist = safe_call("generate_action_checklist", plan, fallback="Checklist unavailable.")
    ops_handoff = safe_call("generate_ops_handoff", plan, extracted, fallback="Operations handoff unavailable.")
    email_ready_reply = safe_call("generate_email_ready_reply", plan, fallback="Email-ready reply unavailable.")
    task_digest = safe_call("generate_task_digest", plan, extracted, fallback="Task digest unavailable.")
    baseline_draft = safe_call("draft_response_with_mode", plan, False, fallback="Baseline draft unavailable.")
    enhanced_draft = safe_call("draft_response_with_mode", plan, True, fallback="Enhanced draft unavailable.")

    return {
        "source_text": text,
        "extracted": extracted,
        "plan": plan,
        "summary": summary,
        "short_summary": short_summary,
        "recommended_next_action": recommended_next_action,
        "checklist": checklist,
        "ops_handoff": ops_handoff,
        "email_ready_reply": email_ready_reply,
        "task_digest": task_digest,
        "baseline_draft": baseline_draft,
        "enhanced_draft": enhanced_draft,
    }


def compute_case_confidence(extracted: dict, plan) -> tuple:
    confidence_map = extracted.get("confidence", {})
    scores = []

    for category in ["deadlines", "requested_documents", "action_items"]:
        scores.extend(confidence_map.get(category, {}).values())

    signal_count = (
        len(extracted.get("deadlines", []))
        + len(extracted.get("requested_documents", []))
        + len(extracted.get("action_items", []))
    )

    if not scores or len(plan.tasks) == 0:
        return "low", 0.35

    avg = sum(scores) / len(scores)

    if signal_count >= 5 and avg >= 0.82:
        return "high", avg
    if signal_count >= 2 and avg >= 0.70:
        return "medium", avg
    return "low", avg


def badge_html(label: str) -> str:
    styles = {
        "high": ("#dcfce7", "#166534"),
        "medium": ("#fef3c7", "#92400e"),
        "low": ("#fee2e2", "#991b1b"),
    }
    bg, fg = styles.get(label, ("#f3f4f6", "#111827"))
    return f"<span style='background:{bg};color:{fg};padding:6px 10px;border-radius:999px;font-size:14px;font-weight:700;'>{label}</span>"


def render_task_card(task):
    color = {
        "high": "#ef4444",
        "medium": "#f59e0b",
        "low": "#9ca3af",
    }.get(getattr(task, "priority", "low"), "#9ca3af")

    status = getattr(task, "status", "ready")
    workflow = getattr(task, "workflow_type", "general")
    source = getattr(task, "source", "")
    urgency = getattr(task, "urgency_score", 0)
    depends_on = getattr(task, "depends_on", [])
    blocking_reason = getattr(task, "blocking_reason", "")

    depends_html = ""
    if depends_on:
        depends_html = f"<div style='margin-top:10px;font-size:15px;color:#6b7280;'><strong>Depends on:</strong> {', '.join(depends_on)}</div>"

    blocking_html = ""
    if blocking_reason:
        blocking_html = f"<div style='margin-top:10px;font-size:15px;color:#92400e;'><strong>Blocked because:</strong> {blocking_reason}</div>"

    st.markdown(
        f"""
<div style="border-left:8px solid {color};border-radius:16px;padding:18px 18px;margin-bottom:14px;background:#ffffff;border:1px solid #e5e7eb;">
  <div style="font-weight:800;font-size:20px;line-height:1.4;">{task.task}</div>
  <div style="margin-top:10px;font-size:15px;color:#4b5563;">
    <strong>Status:</strong> {status} &nbsp;&nbsp;•&nbsp;&nbsp;
    <strong>Workflow:</strong> {workflow} &nbsp;&nbsp;•&nbsp;&nbsp;
    <strong>Source:</strong> {source} &nbsp;&nbsp;•&nbsp;&nbsp;
    <strong>Priority:</strong> {getattr(task, "priority", "")} &nbsp;&nbsp;•&nbsp;&nbsp;
    <strong>Urgency:</strong> {urgency}
  </div>
  {depends_html}
  {blocking_html}
</div>
""",
        unsafe_allow_html=True,
    )


def render_list_section(title: str, items, confidence_map=None):
    st.markdown(f"### {title}")
    if not items:
        st.caption("None found.")
        return

    for item in items:
        score_html = ""
        if confidence_map is not None:
            score = confidence_map.get(item, 0.0)
            if score >= 0.9:
                label = "high"
            elif score >= 0.75:
                label = "medium"
            else:
                label = "low"
            score_html = badge_html(label)

        st.markdown(
            f"""
<div style="border:1px solid #e5e7eb;border-radius:14px;padding:14px 16px;margin-bottom:10px;background:white;display:flex;justify-content:space-between;align-items:center;gap:16px;">
  <div style="font-weight:700;font-size:18px;line-height:1.4;">{item}</div>
  <div>{score_html}</div>
</div>
""",
            unsafe_allow_html=True,
        )


def render_case_results(results, title="Results"):
    extracted = results["extracted"]
    plan = results["plan"]

    deadlines = extracted.get("deadlines", [])
    documents = extracted.get("requested_documents", [])
    actions = extracted.get("action_items", [])
    confidence = extracted.get("confidence", {})

    case_confidence_label, case_confidence_score = compute_case_confidence(extracted, plan)

    st.markdown(f"## {title}")

    st.markdown(
        f"""
<div style="border:1px solid #dbeafe;border-radius:16px;padding:18px 20px;background:#eff6ff;margin-bottom:16px;">
  <div style="font-size:15px;color:#1d4ed8;margin-bottom:8px;font-weight:700;">Next Best Action</div>
  <div style="font-size:24px;font-weight:800;color:#1e3a8a;line-height:1.4;">{results["recommended_next_action"]}</div>
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
<div style="border:1px solid #e5e7eb;border-radius:16px;padding:18px 20px;background:#ffffff;margin-bottom:16px;">
  <div style="font-size:15px;color:#6b7280;margin-bottom:8px;font-weight:700;">Overall System Confidence</div>
  <div style="font-size:24px;font-weight:800;color:#111827;line-height:1.4;">{case_confidence_label} ({case_confidence_score:.2f})</div>
</div>
""",
        unsafe_allow_html=True,
    )

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Deadlines", len(deadlines))
    m2.metric("Documents", len(documents))
    m3.metric("Actions", len(actions))
    m4.metric("Tasks", len(plan.tasks))

    st.markdown("### Original Input")
    st.text_area(f"{title} Source Text", results["source_text"], height=220)

    c1, c2, c3 = st.columns(3)
    with c1:
        render_list_section("Deadlines", deadlines, confidence.get("deadlines", {}))
    with c2:
        render_list_section("Requested Documents", documents, confidence.get("requested_documents", {}))
    with c3:
        render_list_section("Action Items", actions, confidence.get("action_items", {}))

    st.markdown("### Task Plan")
    if not plan.tasks:
        st.info("No task plan was generated from this input.")
    else:
        for task in plan.tasks:
            render_task_card(task)

    st.markdown("### Outputs")
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(
        [
            "Short Summary",
            "Email Reply",
            "Task Digest",
            "Full Summary",
            "Enhanced Draft",
            "Checklist",
            "Operations Handoff",
        ]
    )

    with tab1:
        value = st.text_area(f"{title} Short Summary", results["short_summary"], height=280)
        st.download_button("Export Short Summary", value, "visaflow_short_summary_export.txt", "text/plain")

    with tab2:
        value = st.text_area(f"{title} Email Reply", results["email_ready_reply"], height=320)
        st.download_button("Export Email Reply", value, "visaflow_email_ready_reply_export.txt", "text/plain")

    with tab3:
        value = st.text_area(f"{title} Task Digest", results["task_digest"], height=320)
        st.download_button("Export Task Digest", value, "visaflow_task_digest_export.txt", "text/plain")

    with tab4:
        value = st.text_area(f"{title} Full Summary", results["summary"], height=320)
        st.download_button("Export Full Summary", value, "visaflow_summary_export.txt", "text/plain")

    with tab5:
        value = st.text_area(f"{title} Enhanced Draft", results["enhanced_draft"], height=360)
        st.download_button("Export Enhanced Draft", value, "visaflow_enhanced_draft_export.txt", "text/plain")

    with tab6:
        value = st.text_area(f"{title} Checklist", results["checklist"], height=360)
        st.download_button("Export Checklist", value, "visaflow_checklist_export.txt", "text/plain")

    with tab7:
        value = st.text_area(f"{title} Operations Handoff", results["ops_handoff"], height=360)
        st.download_button("Export Operations Handoff", value, "visaflow_operations_handoff_export.txt", "text/plain")


def get_input_text(prefix: str):
    sample_files = sorted([p.name for p in SAMPLES_DIR.glob("*.txt")])

    mode = st.radio(
        f"{prefix} input type",
        ["Demo preset", "Paste text", "Upload file", "Sample file"],
        horizontal=True,
        key=f"{prefix}_mode",
    )

    if mode == "Demo preset":
        preset = st.selectbox(
            f"{prefix} preset",
            list(DEMO_PRESETS.keys()),
            index=0,
            key=f"{prefix}_preset",
        )
        st.info(DEMO_PRESETS[preset]["note"])
        return DEMO_PRESETS[preset]["text"]

    if mode == "Paste text":
        return st.text_area(
            f"{prefix} pasted text",
            height=220,
            placeholder="Paste the full email or message here...",
            key=f"{prefix}_paste",
        )

    if mode == "Upload file":
        uploaded = st.file_uploader(
            f"{prefix} upload a .txt file",
            type=["txt"],
            key=f"{prefix}_upload",
        )
        if uploaded is not None:
            return uploaded.read().decode("utf-8").strip()
        return ""

    if mode == "Sample file":
        selected_file = st.selectbox(
            f"{prefix} sample file",
            sample_files,
            key=f"{prefix}_sample",
        )
        if selected_file:
            document = load_document(SAMPLES_DIR / selected_file)
            return document.text
        return ""

    return ""


st.set_page_config(page_title=APP_TITLE, layout="wide")

st.markdown(
    """
<style>
.block-container {
    max-width: 1300px;
    padding-top: 1.2rem;
    padding-bottom: 3rem;
}
div[data-testid="stMetric"] {
    background: #ffffff;
    border: 1px solid #e5e7eb;
    padding: 16px;
    border-radius: 16px;
}
div[data-testid="stMetric"] label {
    font-size: 16px !important;
}
div[data-testid="stMetricValue"] {
    font-size: 28px !important;
}
textarea, input, select, button {
    font-size: 18px !important;
}
p, li, label, div {
    font-size: 17px;
}
</style>
""",
    unsafe_allow_html=True,
)

if "single_results" not in st.session_state:
    st.session_state.single_results = None
if "compare_left_results" not in st.session_state:
    st.session_state.compare_left_results = None
if "compare_right_results" not in st.session_state:
    st.session_state.compare_right_results = None

st.title(APP_TITLE)
st.markdown(f"### {APP_SUBTITLE}")
st.markdown(
    """
This app helps turn administrative messages into structured workflow support.

Use it in a simple order:

**1. Choose a mode**  
**2. Provide one or two inputs**  
**3. Run the workflow**  
**4. Review the extracted requirements, task plan, and outputs**
"""
)

st.divider()

mode = st.radio(
    "Choose a mode",
    ["Single Message", "Compare Two Messages"],
    horizontal=True,
)

if mode == "Single Message":
    st.markdown("## Step 1 — Provide one input")
    source_text = get_input_text("Single")

    st.markdown("## Step 2 — Run")
    c1, c2 = st.columns([1, 1])
    with c1:
        run_single = st.button("Run Single Workflow", use_container_width=True)
    with c2:
        clear_single = st.button("Clear Single Results", use_container_width=True)

    if clear_single:
        st.session_state.single_results = None

    if run_single:
        if not source_text.strip():
            st.warning("Please provide some input before running the workflow.")
        else:
            st.session_state.single_results = run_pipeline_from_text(source_text.strip())

    st.divider()
    st.markdown("## Step 3 — Review results")

    if st.session_state.single_results is None:
        st.info("No results yet. Add an input above and click Run Single Workflow.")
    else:
        render_case_results(st.session_state.single_results, "Single Message Results")

else:
    st.markdown("## Step 1 — Provide two inputs to compare")

    left_col, right_col = st.columns(2)
    with left_col:
        st.markdown("### Left Input")
        left_text = get_input_text("Left")
    with right_col:
        st.markdown("### Right Input")
        right_text = get_input_text("Right")

    st.markdown("## Step 2 — Run")
    c1, c2 = st.columns([1, 1])
    with c1:
        run_compare = st.button("Run Comparison", use_container_width=True)
    with c2:
        clear_compare = st.button("Clear Comparison Results", use_container_width=True)

    if clear_compare:
        st.session_state.compare_left_results = None
        st.session_state.compare_right_results = None

    if run_compare:
        if not left_text.strip() or not right_text.strip():
            st.warning("Please provide both inputs before running the comparison.")
        else:
            st.session_state.compare_left_results = run_pipeline_from_text(left_text.strip())
            st.session_state.compare_right_results = run_pipeline_from_text(right_text.strip())

    st.divider()
    st.markdown("## Step 3 — Review comparison results")

    if st.session_state.compare_left_results is None or st.session_state.compare_right_results is None:
        st.info("No comparison results yet. Add two inputs above and click Run Comparison.")
    else:
        left_results = st.session_state.compare_left_results
        right_results = st.session_state.compare_right_results

        left_plan = left_results["plan"]
        right_plan = right_results["plan"]

        left_extracted = left_results["extracted"]
        right_extracted = right_results["extracted"]

        st.markdown("### Comparison Summary")
        summary_lines = []

        left_deadlines = len(left_extracted.get("deadlines", []))
        right_deadlines = len(right_extracted.get("deadlines", []))
        left_docs = len(left_extracted.get("requested_documents", []))
        right_docs = len(right_extracted.get("requested_documents", []))
        left_tasks = len(left_plan.tasks)
        right_tasks = len(right_plan.tasks)

        def compare_line(label, left_val, right_val):
            if left_val > right_val:
                return f"- Left input has more {label}: {left_val} vs {right_val}"
            if right_val > left_val:
                return f"- Right input has more {label}: {right_val} vs {left_val}"
            return f"- Both inputs have the same number of {label}: {left_val}"

        summary_lines.append(compare_line("deadlines", left_deadlines, right_deadlines))
        summary_lines.append(compare_line("documents", left_docs, right_docs))
        summary_lines.append(compare_line("tasks", left_tasks, right_tasks))

        st.markdown("\n".join(summary_lines))

        col1, col2 = st.columns(2)
        with col1:
            render_case_results(left_results, "Left Results")
        with col2:
            render_case_results(right_results, "Right Results")
