import streamlit as st

from visaflow.config import SAMPLES_DIR
from visaflow.ingestion.loaders import load_document
from visaflow.extraction.extractors import extract_information
from visaflow.planning.planner import build_task_plan
from visaflow.drafting.drafter import (
    draft_response_with_mode,
    generate_next_step_summary,
    generate_action_checklist,
    generate_recommended_next_action,
    generate_ops_handoff,
)


DEFAULT_PRESET = "Mixed admin case"

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
    "Escalated admin case": {
        "text": """Subject: Urgent follow-up on housing, financial aid, and immigration items

Hello Nesib,

We are still missing your signed housing agreement, updated bank statement, current passport copy, current I-20, and statement of support.

Please upload all materials through the student portal by June 10, 2026. You should also reply to this email by June 8, 2026 if you expect any delay. Once everything has been uploaded, please confirm completion so we can finish the review.

Best,
Student Services and Financial Support""",
        "description": "Shows a denser case with multiple deadlines, document requests, and follow-up actions.",
    },
    "Weak noisy case": {
        "text": """Subject: quick follow up

hi, just checking in on the file. send what you can soon and let us know if anything changed.

thanks""",
        "description": "Shows how the system behaves on weak or incomplete administrative text.",
    },
}

DEMO_SCRIPT = [
    "Start with Mixed admin case to show the strongest clean end-to-end example.",
    "Use Escalated admin case to show heavier multi-deadline handling.",
    "Use Housing follow-up or Financial aid review if you want a simpler single-theme example.",
    "Use Immigration update to highlight workflow tagging.",
    "Use Weak noisy case to show graceful behavior on incomplete input.",
    "End with pasted text or upload mode only if you want a live input example.",
]


def run_pipeline_from_text(text: str):
    extracted = extract_information(text)
    plan = build_task_plan(extracted)
    summary = generate_next_step_summary(plan)
    recommended_next_action = generate_recommended_next_action(plan)
    checklist = generate_action_checklist(plan)
    ops_handoff = generate_ops_handoff(plan, extracted)
    task_digest = generate_task_digest(plan, extracted)
    email_ready_reply = generate_email_ready_reply(plan)
    baseline_draft = draft_response_with_mode(plan, enhanced=False)
    enhanced_draft = draft_response_with_mode(plan, enhanced=True)
    return {
        "source_text": text,
        "extracted": extracted,
        "plan": plan,
        "summary": summary,
        "recommended_next_action": recommended_next_action,
        "checklist": checklist,
        "ops_handoff": ops_handoff,
        "task_digest": task_digest,
        "email_ready_reply": email_ready_reply,
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
        st.caption(f"No {title.lower()} found.")
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

    blocking = ""
    if getattr(task, "blocking_reason", ""):
        blocking = f"<div style='margin-top:6px;font-size:12px;color:#92400e;'>Blocked because: {task.blocking_reason}</div>"

    st.markdown(
        f"""
<div style="border-left:6px solid {color};border-radius:12px;padding:14px 16px;margin-bottom:12px;background:#ffffff;border:1px solid #e5e7eb;">
  <div style="display:flex;justify-content:space-between;align-items:center;gap:12px;">
    <div style="font-weight:600;font-size:15px;">{task.task}</div>
    <div>{status_badge(task.status)}</div>
  </div>
  <div style="margin-top:8px;font-size:12px;color:#6b7280;">
    workflow: {task.workflow_type} • source: {task.source} • priority: {task.priority} • urgency: {task.urgency_score}
  </div>
  {depends}
  {blocking}
</div>
""",
        unsafe_allow_html=True,
    )


def render_comparison_column(title: str, result: dict):
    extracted = result["extracted"]
    plan = result["plan"]
    summary = result["summary"]
    confidence = extracted.get("confidence", {})

    deadlines = extracted.get("deadlines", [])
    documents = extracted.get("requested_documents", [])
    actions = extracted.get("action_items", [])

    st.markdown(f"### {title}")
    st.text_area(f"{title} summary", summary, height=180)
    a, b, c = st.columns(3)
    a.metric("Deadlines", len(deadlines))
    b.metric("Documents", len(documents))
    c.metric("Tasks", len(plan.tasks))

    if len(deadlines) + len(documents) + len(actions) == 0:
        st.warning("This case produced very little structured signal.")
    else:
        render_compact_findings("Deadlines", deadlines[:3], confidence.get("deadlines", {}))
        render_compact_findings("Requested Documents", documents[:4], confidence.get("requested_documents", {}))
        render_compact_findings("Action Items", actions[:3], confidence.get("action_items", {}))


def render_comparison_summary(left_name: str, left_result: dict, right_name: str, right_result: dict):
    left_extracted = left_result["extracted"]
    right_extracted = right_result["extracted"]
    left_plan = left_result["plan"]
    right_plan = right_result["plan"]

    left_deadlines = len(left_extracted.get("deadlines", []))
    right_deadlines = len(right_extracted.get("deadlines", []))
    left_documents = len(left_extracted.get("requested_documents", []))
    right_documents = len(right_extracted.get("requested_documents", []))
    left_tasks = len(left_plan.tasks)
    right_tasks = len(right_plan.tasks)

    left_workflows = set(task.workflow_type for task in left_plan.tasks)
    right_workflows = set(task.workflow_type for task in right_plan.tasks)

    st.markdown("### Comparison Highlights")

    def compare_line(label, left_val, right_val):
        if left_val > right_val:
            return f"- **{left_name}** has more {label}: {left_val} vs {right_val}"
        if right_val > left_val:
            return f"- **{right_name}** has more {label}: {right_val} vs {left_val}"
        return f"- Both cases have the same number of {label}: {left_val}"

    lines = [
        compare_line("deadlines", left_deadlines, right_deadlines),
        compare_line("requested documents", left_documents, right_documents),
        compare_line("planned tasks", left_tasks, right_tasks),
    ]

    left_only = sorted(left_workflows - right_workflows)
    right_only = sorted(right_workflows - left_workflows)

    if left_only:
        lines.append(f"- **{left_name}** uniquely includes workflows: {', '.join(left_only)}")
    if right_only:
        lines.append(f"- **{right_name}** uniquely includes workflows: {', '.join(right_only)}")
    if not left_only and not right_only:
        lines.append("- Both cases cover the same workflow categories.")

    st.markdown(
        """
<div style="border:1px solid #dbeafe;border-radius:14px;padding:14px 16px;background:#eff6ff;margin-bottom:14px;">
"""
        + "<br>".join(lines) +
        """
</div>
""",
        unsafe_allow_html=True,
    )


def assess_input_quality(source_text: str, extracted: dict, plan) -> str:
    signal_count = (
        len(extracted.get("deadlines", []))
        + len(extracted.get("requested_documents", []))
        + len(extracted.get("action_items", []))
    )

    if len(source_text.split()) < 12:
        return "very_low"
    if signal_count == 0:
        return "low"
    if signal_count <= 2 and len(plan.tasks) <= 2:
        return "medium"
    return "good"


def compute_case_confidence(extracted: dict, plan) -> tuple:
    confidence_map = extracted.get("confidence", {})
    all_scores = []

    for category in ["deadlines", "requested_documents", "action_items"]:
        all_scores.extend(confidence_map.get(category, {}).values())

    signal_count = (
        len(extracted.get("deadlines", []))
        + len(extracted.get("requested_documents", []))
        + len(extracted.get("action_items", []))
    )

    if not all_scores or len(plan.tasks) == 0:
        return ("low", 0.35)

    avg_score = sum(all_scores) / len(all_scores)

    if signal_count >= 5 and avg_score >= 0.82:
        return ("high", avg_score)
    if signal_count >= 2 and avg_score >= 0.70:
        return ("medium", avg_score)
    return ("low", avg_score)


def classify_weak_case(source_text: str, extracted: dict, plan) -> str:
    lowered = source_text.lower()
    signal_count = (
        len(extracted.get("deadlines", []))
        + len(extracted.get("requested_documents", []))
        + len(extracted.get("action_items", []))
    )

    if len(plan.tasks) > 0 or signal_count >= 3:
        return "not_weak"

    if any(term in lowered for term in ["checking in", "follow up", "quick follow up", "just checking"]):
        return "generic_follow_up"

    if any(term in lowered for term in ["send what you can", "soon", "let us know if anything changed"]):
        return "soft_reminder"

    return "incomplete_request"


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
    presenter_mode = st.checkbox("Presenter mode", value=True)
    minimal_view = st.checkbox("Minimal view", value=False)
    comparison_mode = st.checkbox("Comparison mode", value=False)
    show_demo_script = st.checkbox("Show demo script panel", value=True)
    input_mode = st.radio(
        "Input mode",
        ["Demo preset", "Sample file", "Paste text", "Upload file"],
        index=0,
    )

    selected_preset = None
    selected_file = None
    pasted_text = ""
    uploaded_file = None

    preset_index = list(DEMO_PRESETS.keys()).index(DEFAULT_PRESET)

    if comparison_mode:
        compare_left = st.selectbox("Left preset", list(DEMO_PRESETS.keys()), index=preset_index, key="compare_left")
        compare_right = st.selectbox("Right preset", list(DEMO_PRESETS.keys()), index=0, key="compare_right")
    else:
        if input_mode == "Demo preset":
            selected_preset = st.selectbox("Choose a preset", list(DEMO_PRESETS.keys()), index=preset_index)
            st.caption(f"Recommended: {DEFAULT_PRESET}")
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

Recommended first run: **Mixed admin case**
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
    current_mode_label = "Comparison" if comparison_mode else input_mode
    current_case_label = "Preset comparison" if comparison_mode else (selected_preset if input_mode == "Demo preset" and selected_preset else "Custom input")
    st.markdown(
        f"""
<div style="border:1px solid #e5e7eb;border-radius:16px;padding:16px;background:#ffffff;">
  <div style="font-size:12px;color:#6b7280;margin-bottom:8px;">Current state</div>
  <div style="font-size:18px;font-weight:700;margin-bottom:8px;">{current_case_label}</div>
  <div style="font-size:13px;color:#4b5563;">Mode: {current_mode_label}</div>
  <div style="font-size:13px;color:#4b5563;">Presenter mode: {"on" if presenter_mode else "off"}</div>
  <div style="font-size:13px;color:#4b5563;">Minimal view: {"on" if minimal_view else "off"}</div>
  <div style="font-size:13px;color:#4b5563;">Suggested preset: {DEFAULT_PRESET}</div>
</div>
""",
        unsafe_allow_html=True,
    )

st.divider()

control_left, control_mid, control_right = st.columns([1.2, 1.2, 0.8])
with control_left:
    st.markdown("### Demo controls")
    st.caption("Use quick launch buttons or the sidebar controls during the demo.")
with control_mid:
    if st.session_state.results is None:
        st.info("No results loaded yet.")
    else:
        st.success("Current results are loaded.")
with control_right:
    if st.button("Reset demo state", use_container_width=True):
        st.session_state.results = None

if not minimal_view:
    with st.expander("Demo Comparison Guide", expanded=False):
        st.markdown("### Recommended comparison pair")
        st.write(f'- Left case: **{BEST_COMPARISON_GUIDE["left"]}**')
        st.write(f'- Right case: **{BEST_COMPARISON_GUIDE["right"]}**')
        st.write(f'- Why it works: {BEST_COMPARISON_GUIDE["reason"]}')

    with st.expander("Final Demo Checklist", expanded=False):
        st.markdown("### Recommended recording flow")
        for i, step in enumerate(FINAL_DEMO_CHECKLIST, start=1):
            st.write(f"{i}. {step}")

if show_demo_script and not minimal_view:
    with st.expander("Demo guide", expanded=False):
        st.markdown("### Suggested flow")
        for i, step in enumerate(DEMO_SCRIPT, start=1):
            st.write(f"{i}. {step}")
        st.markdown("### Preset explanations")
        for name, preset in DEMO_PRESETS.items():
            st.write(f"- **{name}**: {preset['description']}")

st.subheader("Preset Notes")

if not comparison_mode and input_mode == "Demo preset" and selected_preset:
    st.markdown(
        f"""
<div style="border:1px solid #e5e7eb;border-radius:14px;padding:14px 16px;background:#ffffff;margin-bottom:16px;">
  <div style="font-size:12px;color:#6b7280;margin-bottom:6px;">Selected preset</div>
  <div style="font-size:16px;font-weight:700;margin-bottom:8px;">{selected_preset}</div>
  <div style="font-size:13px;color:#4b5563;">{PRESET_NOTES.get(selected_preset, "")}</div>
</div>
""",
        unsafe_allow_html=True,
    )

st.subheader("Quick Launch Presets")
q1, q2, q3, q4, q5, q6 = st.columns(6)
preset_names = [
    "Mixed admin case",
    "Escalated admin case",
    "Housing follow-up",
    "Financial aid review",
    "Immigration update",
    "Weak noisy case",
]
quick_clicked = None

if q1.button(preset_names[0], use_container_width=True):
    quick_clicked = preset_names[0]
if q2.button(preset_names[1], use_container_width=True):
    quick_clicked = preset_names[1]
if q3.button(preset_names[2], use_container_width=True):
    quick_clicked = preset_names[2]
if q4.button(preset_names[3], use_container_width=True):
    quick_clicked = preset_names[3]
if q5.button(preset_names[4], use_container_width=True):
    quick_clicked = preset_names[4]
if q6.button(preset_names[5], use_container_width=True):
    quick_clicked = preset_names[5]

if clear_results:
    st.session_state.results = None

if quick_clicked is not None:
    st.session_state.results = run_pipeline_from_text(DEMO_PRESETS[quick_clicked]["text"])

if run_pipeline:
    if comparison_mode:
        st.session_state.results = {
            "comparison": True,
            "left": run_pipeline_from_text(DEMO_PRESETS[compare_left]["text"]),
            "right": run_pipeline_from_text(DEMO_PRESETS[compare_right]["text"]),
            "left_name": compare_left,
            "right_name": compare_right,
        }
    else:
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

if results is not None and isinstance(results, dict) and results.get("comparison"):
    st.subheader("Case Comparison")
    render_comparison_summary(results["left_name"], results["left"], results["right_name"], results["right"])
    left_col, right_col = st.columns(2)
    with left_col:
        render_comparison_column(results["left_name"], results["left"])
    with right_col:
        render_comparison_column(results["right_name"], results["right"])

elif results is not None:
    source_text = results["source_text"]
    extracted = results["extracted"]
    plan = results["plan"]
    summary = results["summary"]
    recommended_next_action = results["recommended_next_action"]
    checklist = results["checklist"]
    ops_handoff = results["ops_handoff"]
    task_digest = results["task_digest"]
    email_ready_reply = results["email_ready_reply"]
    baseline_draft = results["baseline_draft"]
    enhanced_draft = results["enhanced_draft"]

    deadlines = extracted.get("deadlines", [])
    documents = extracted.get("requested_documents", [])
    actions = extracted.get("action_items", [])
    evidence = extracted.get("evidence", {})
    confidence = extracted.get("confidence", {})

    quality = assess_input_quality(source_text, extracted, plan)
    case_confidence_label, case_confidence_score = compute_case_confidence(extracted, plan)
    weak_case_label = classify_weak_case(source_text, extracted, plan)

    if quality == "very_low":
        st.warning("This input is very short. The app may not have enough information to build a strong workflow.")
    elif quality == "low":
        st.warning("Only limited structured information was found. Results may be incomplete.")
    elif quality == "medium":
        st.info("A partial workflow was detected. This is usable, but likely not a complete administrative request.")

    if weak_case_label == "generic_follow_up":
        st.info("This looks like a generic follow-up rather than a detailed administrative request.")
    elif weak_case_label == "soft_reminder":
        st.info("This looks like a soft reminder message with limited operational detail.")
    elif weak_case_label == "incomplete_request":
        st.info("This looks like an incomplete request that would benefit from the full email thread.")

    urgent_count = len([task for task in plan.tasks if task.status == "urgent"])
    ready_count = len([task for task in plan.tasks if task.status == "ready"])
    blocked_count = len([task for task in plan.tasks if task.status == "blocked"])
    workflow_count = len(set(task.workflow_type for task in plan.tasks))

    st.subheader("Overview")
    st.markdown(
        f"""
<div style="border:1px solid #dbeafe;border-radius:14px;padding:14px 16px;background:#eff6ff;margin-bottom:14px;">
  <div style="font-size:12px;color:#1d4ed8;margin-bottom:6px;">Next best action</div>
  <div style="font-size:16px;font-weight:700;color:#1e3a8a;">{recommended_next_action}</div>
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
<div style="border:1px solid #e5e7eb;border-radius:14px;padding:14px 16px;background:#ffffff;margin-bottom:14px;">
  <div style="font-size:12px;color:#6b7280;margin-bottom:6px;">Overall system confidence</div>
  <div style="font-size:16px;font-weight:700;color:#111827;">{case_confidence_label} ({case_confidence_score:.2f})</div>
</div>
""",
        unsafe_allow_html=True,
    )

    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Deadlines", len(deadlines))
    m2.metric("Documents", len(documents))
    m3.metric("Actions", len(actions))
    m4.metric("Urgent / Ready / Blocked", f"{urgent_count} / {ready_count} / {blocked_count}")
    m5.metric("Workflows", workflow_count)

    st.divider()

    if minimal_view:
        left, right = st.columns([1.0, 1.0])
        with left:
            st.subheader("Summary")
            st.text_area("Summary", summary, height=260)
        with right:
            st.subheader("Task Plan")
            if len(plan.tasks) == 0:
                st.info("No task plan was generated from this input.")
            else:
                for task in plan.tasks[:8]:
                    render_task_card(task)

        st.divider()
        st.subheader("Outputs")

    st.markdown("### Task Digest")
    task_digest_text = st.text_area("Task Digest", task_digest, height=220)
    st.download_button(
        label="Export task digest",
        data=task_digest_text,
        file_name="visaflow_task_digest_export.txt",
        mime="text/plain",
        use_container_width=True,
        key="download_task_digest",
    )

        tab1, tab2, tab3 = st.tabs(["Enhanced Draft", "Checklist", "Operations Handoff"])

        with tab1:
            enhanced_editable = st.text_area("Enhanced Draft", enhanced_draft, height=320)
            st.download_button(
                label="Export enhanced draft",
                data=enhanced_editable,
                file_name="visaflow_enhanced_draft_export.txt",
                mime="text/plain",
                use_container_width=True,
                key="download_enhanced_minimal",
            )

        with tab2:
            checklist_text = st.text_area("Checklist", checklist, height=320)
            st.download_button(
                label="Export checklist",
                data=checklist_text,
                file_name="visaflow_checklist_export.txt",
                mime="text/plain",
                use_container_width=True,
                key="download_checklist_minimal",
            )

        with tab3:
            ops_text = st.text_area("Operations Handoff", ops_handoff, height=320)
            st.download_button(
                label="Download ops handoff",
                data=ops_text,
                file_name="visaflow_operations_handoff_export.txt",
                mime="text/plain",
                use_container_width=True,
                key="download_ops_handoff_minimal",
            )

    else:
        left, right = st.columns([1.15, 0.85])
        with left:
            st.subheader("Source")
            st.text_area("Input", source_text, height=260)
        with right:
            st.subheader("Summary")
            st.text_area("Summary", summary, height=260)

        st.divider()

        st.subheader("Extraction Overview")

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

        if len(plan.tasks) == 0:
            st.info("No task plan was generated from this input.")
        else:
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

            if len(plan.tasks) > 0:
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
        st.subheader("Outputs")

    st.markdown("### Task Digest")
    task_digest_text = st.text_area("Task Digest", task_digest, height=220)
    st.download_button(
        label="Export task digest",
        data=task_digest_text,
        file_name="visaflow_task_digest_export.txt",
        mime="text/plain",
        use_container_width=True,
        key="download_task_digest",
    )


        if presenter_mode:
            tab1, tab2, tab3 = st.tabs(["Enhanced Draft", "Checklist", "Operations Handoff"])
            with tab1:
                enhanced_editable = st.text_area("Enhanced Draft", enhanced_draft, height=320)
                st.download_button(
                    label="Export enhanced draft",
                    data=enhanced_editable,
                    file_name="visaflow_enhanced_draft_export.txt",
                    mime="text/plain",
                    use_container_width=True,
                    key="download_enhanced_presenter",
                )
            with tab2:
                checklist_text = st.text_area("Checklist", checklist, height=320)
                st.download_button(
                    label="Export checklist",
                    data=checklist_text,
                    file_name="visaflow_checklist_export.txt",
                    mime="text/plain",
                    use_container_width=True,
                    key="download_checklist_presenter",
                )
            with tab3:
                ops_text = st.text_area("Operations Handoff", ops_handoff, height=320)
                st.download_button(
                    label="Download ops handoff",
                    data=ops_text,
                    file_name="visaflow_operations_handoff_export.txt",
                    mime="text/plain",
                    use_container_width=True,
                    key="download_ops_handoff_presenter",
                )
        else:
            tab1, tab2, tab3, tab4, tab5 = st.tabs(["Summary", "Baseline Draft", "Enhanced Draft", "Checklist", "Operations Handoff"])

            with tab1:
                st.text_area("Summary view", summary, height=280)
                st.download_button(
                    label="Export full summary",
                    data=summary,
                    file_name="visaflow_full_summary_export.txt",
                    mime="text/plain",
                    use_container_width=True,
                    key="download_summary",
                )

            with tab2:
                baseline_editable = st.text_area("Baseline Draft", baseline_draft, height=320)
                st.download_button(
                    label="Export baseline draft",
                    data=baseline_editable,
                    file_name="visaflow_baseline_draft_export.txt",
                    mime="text/plain",
                    use_container_width=True,
                    key="download_baseline",
                )

            with tab3:
                enhanced_editable = st.text_area("Enhanced Draft", enhanced_draft, height=320)
                st.download_button(
                    label="Export enhanced draft",
                    data=enhanced_editable,
                    file_name="visaflow_enhanced_draft_export.txt",
                    mime="text/plain",
                    use_container_width=True,
                    key="download_enhanced",
                )

            with tab5:
                checklist_text = st.text_area("Checklist", checklist, height=320)
                st.download_button(
                    label="Export checklist",
                    data=checklist_text,
                    file_name="visaflow_checklist_export.txt",
                    mime="text/plain",
                    use_container_width=True,
                    key="download_checklist",
                )

            with tab6:
                ops_text = st.text_area("Operations Handoff", ops_handoff, height=320)
                st.download_button(
                    label="Download ops handoff",
                    data=ops_text,
                    file_name="visaflow_operations_handoff_export.txt",
                    mime="text/plain",
                    use_container_width=True,
                    key="download_ops_handoff",
                )
else:
    st.info("Choose a preset, sample file, pasted text, or uploaded file, then click Run pipeline, or use a Quick Launch button.")
