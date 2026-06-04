import streamlit as st
from pathlib import Path
from visaflow.main import run_pipeline_from_text
from visaflow.ingestion.loaders import load_document
from visaflow.config import SAMPLES_DIR, DEMO_PRESETS, APP_TITLE, APP_SUBTITLE
from visaflow.utils.render import compute_case_confidence

st.set_page_config(page_title=APP_TITLE, page_icon="🌏", layout="wide")

st.markdown("""
<style>
.block-container { max-width: 1300px; padding-top: 1.2rem; padding-bottom: 3rem; }
div[data-testid="stMetric"] {
    background: #ffffff; border: 1px solid #e5e7eb;
    padding: 16px; border-radius: 16px;
}
div[data-testid="stMetric"] label { font-size: 16px !important; }
div[data-testid="stMetricValue"] { font-size: 28px !important; }
textarea, input, select, button { font-size: 17px !important; }
p, li, label, div { font-size: 16px; }
.visa-tag {
    display: inline-block; background: #dbeafe; color: #1e40af;
    border-radius: 9999px; padding: 2px 12px; font-size: 13px;
    font-weight: 700; margin-right: 6px; margin-bottom: 4px;
}
</style>
""", unsafe_allow_html=True)


def badge_html(label: str) -> str:
    colors = {
        "high": ("#dcfce7", "#166534"),
        "medium": ("#fef9c3", "#854d0e"),
        "low": ("#fee2e2", "#991b1b"),
    }
    bg, fg = colors.get(label, ("#f3f4f6", "#374151"))
    return f'<span style="background:{bg};color:{fg};border-radius:9999px;padding:3px 12px;font-size:13px;font-weight:700;">{label.upper()}</span>'


def render_list_section(title, items, confidence_map=None):
    st.markdown(f"**{title}** ({len(items)})")
    if not items:
        st.caption("None detected.")
        return
    for item in items:
        score = confidence_map.get(item) if confidence_map else None
        score_html = ""
        if score is not None:
            label = "high" if score >= 0.88 else ("medium" if score >= 0.75 else "low")
            score_html = badge_html(label)
        st.markdown(
            f'<div style="border:1px solid #e5e7eb;border-radius:12px;padding:10px 14px;'
            f'margin-bottom:8px;background:white;display:flex;justify-content:space-between;'
            f'align-items:center;gap:12px;">'
            f'<div style="font-weight:600;font-size:16px;">{item}</div>'
            f'<div>{score_html}</div></div>',
            unsafe_allow_html=True,
        )


def render_task_card(task):
    priority_colors = {"high": "#fee2e2", "medium": "#fef9c3", "low": "#f0fdf4"}
    bg = priority_colors.get(getattr(task, "priority", "low"), "#f9fafb")
    deps = getattr(task, "depends_on", [])
    dep_str = f"<br><span style='font-size:13px;color:#6b7280;'>Depends on: {', '.join(deps)}</span>" if deps else ""
    st.markdown(
        f'<div style="border:1px solid #e5e7eb;border-radius:14px;padding:14px 16px;'
        f'margin-bottom:10px;background:{bg};">'
        f'<div style="font-weight:700;font-size:16px;">{getattr(task,"title","Task")}</div>'
        f'<div style="color:#374151;margin-top:4px;">{getattr(task,"description","")}</div>'
        f'{dep_str}</div>',
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
        f'<div style="border:1px solid #bfdbfe;border-radius:16px;padding:18px 20px;'
        f'background:#eff6ff;margin-bottom:16px;">'
        f'<div style="font-size:14px;color:#1d4ed8;margin-bottom:6px;font-weight:700;">🎯 Recommended Next Action</div>'
        f'<div style="font-size:22px;font-weight:800;color:#1e3a8a;">{results["recommended_next_action"]}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        f'<div style="border:1px solid #e5e7eb;border-radius:16px;padding:16px 20px;'
        f'background:#ffffff;margin-bottom:16px;">'
        f'<div style="font-size:14px;color:#6b7280;margin-bottom:4px;font-weight:700;">Overall Confidence</div>'
        f'<div style="font-size:22px;font-weight:800;color:#111827;">{case_confidence_label} ({case_confidence_score:.2f})</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("⏰ Deadlines", len(deadlines))
    m2.metric("📄 Documents", len(documents))
    m3.metric("✅ Actions", len(actions))
    m4.metric("📋 Tasks", len(plan.tasks))

    st.markdown("### Your Input")
    st.text_area("Source Text", results["source_text"], height=180)

    c1, c2, c3 = st.columns(3)
    with c1:
        render_list_section("⏰ Deadlines", deadlines, confidence.get("deadlines", {}))
    with c2:
        render_list_section("📄 Required Documents", documents, confidence.get("requested_documents", {}))
    with c3:
        render_list_section("✅ Action Items", actions, confidence.get("action_items", {}))

    st.markdown("### Task Plan")
    if not plan.tasks:
        st.info("No tasks generated. Try adding more detail to your situation.")
    else:
        for task in plan.tasks:
            render_task_card(task)

    st.markdown("### Outputs")
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "📝 Summary", "📧 Email Draft", "📋 Task Digest",
        "📖 Full Analysis", "✨ Enhanced Draft", "☑️ Checklist", "🤝 Handoff Note"
    ])
    with tab1:
        v = st.text_area("Summary", results["short_summary"], height=260)
        st.download_button("⬇ Export Summary", v, "visaflow_summary.txt", "text/plain")
    with tab2:
        v = st.text_area("Email Draft", results["email_ready_reply"], height=300)
        st.download_button("⬇ Export Email", v, "visaflow_email.txt", "text/plain")
    with tab3:
        v = st.text_area("Task Digest", results["task_digest"], height=300)
        st.download_button("⬇ Export Tasks", v, "visaflow_tasks.txt", "text/plain")
    with tab4:
        v = st.text_area("Full Analysis", results["summary"], height=300)
        st.download_button("⬇ Export Analysis", v, "visaflow_analysis.txt", "text/plain")
    with tab5:
        v = st.text_area("Enhanced Draft", results["enhanced_draft"], height=340)
        st.download_button("⬇ Export Draft", v, "visaflow_draft.txt", "text/plain")
    with tab6:
        v = st.text_area("Checklist", results["checklist"], height=340)
        st.download_button("⬇ Export Checklist", v, "visaflow_checklist.txt", "text/plain")
    with tab7:
        v = st.text_area("Handoff Note", results["ops_handoff"], height=340)
        st.download_button("⬇ Export Handoff", v, "visaflow_handoff.txt", "text/plain")


def get_input_text(prefix: str):
    mode = st.radio(
        f"{prefix} input type",
        ["Demo preset", "Paste your situation", "Upload .txt file"],
        horizontal=True,
        key=f"{prefix}_mode",
    )

    if mode == "Demo preset":
        preset = st.selectbox(
            "Choose a scenario",
            list(DEMO_PRESETS.keys()),
            key=f"{prefix}_preset",
        )
        cfg = DEMO_PRESETS[preset]
        st.info(cfg["note"])
        doc = load_document(SAMPLES_DIR / cfg["file"])
        return doc.text

    if mode == "Paste your situation":
        return st.text_area(
            "Describe your situation, paste an email from your DSO, or ask a career question:",
            height=220,
            placeholder="Example: I'm on F-1 OPT expiring March 2026. My employer wants to file H-1B...",
            key=f"{prefix}_paste",
        )

    if mode == "Upload .txt file":
        uploaded = st.file_uploader("Upload a .txt file", type=["txt"], key=f"{prefix}_upload")
        if uploaded:
            return uploaded.read().decode("utf-8").strip()
        return ""

    return ""


# ── Session state ──
for key in ["single_results", "compare_left_results", "compare_right_results"]:
    if key not in st.session_state:
        st.session_state[key] = None

# ── Header ──
st.markdown(
    '<div style="background:linear-gradient(135deg,#1e3a8a,#1d4ed8);'
    'border-radius:20px;padding:28px 32px;margin-bottom:24px;">'
    '<h1 style="color:white;margin:0;font-size:32px;">🌏 VisaFlow</h1>'
    '<p style="color:#bfdbfe;margin:6px 0 0 0;font-size:17px;">'
    'AI Career &amp; Visa Copilot for International Students</p>'
    '</div>',
    unsafe_allow_html=True,
)

st.markdown("""
**What VisaFlow does for you:**
Paste any DSO email, describe your OPT/H-1B situation, or ask a career question — VisaFlow extracts your deadlines, required documents, and action items, then generates a structured plan, email draft, and checklist tailored to your international student status.

**Try the demo presets** to see real F-1 → OPT → H-1B scenarios.
""")

st.divider()

mode = st.radio("Mode", ["Single Situation", "Compare Two Situations"], horizontal=True)

if mode == "Single Situation":
    st.markdown("## Step 1 — Describe your situation")
    source_text = get_input_text("Single")

    st.markdown("## Step 2 — Run VisaFlow")
    c1, c2 = st.columns([1, 1])
    with c1:
        run_single = st.button("🚀 Run VisaFlow", use_container_width=True)
    with c2:
        clear_single = st.button("🗑 Clear Results", use_container_width=True)

    if clear_single:
        st.session_state.single_results = None
    if run_single:
        if not source_text.strip():
            st.warning("Please add your situation above before running.")
        else:
            with st.spinner("Analyzing your situation..."):
                st.session_state.single_results = run_pipeline_from_text(source_text.strip())

    st.divider()
    st.markdown("## Step 3 — Review your plan")
    if st.session_state.single_results is None:
        st.info("Your results will appear here after you run VisaFlow.")
    else:
        render_case_results(st.session_state.single_results, "Your VisaFlow Analysis")

else:
    st.markdown("## Compare Two Situations")
    left_col, right_col = st.columns(2)
    with left_col:
        st.markdown("### Situation A")
        left_text = get_input_text("Left")
    with right_col:
        st.markdown("### Situation B")
        right_text = get_input_text("Right")

    c1, c2 = st.columns([1, 1])
    with c1:
        run_compare = st.button("🚀 Run Comparison", use_container_width=True)
    with c2:
        clear_compare = st.button("🗑 Clear", use_container_width=True)

    if clear_compare:
        st.session_state.compare_left_results = None
        st.session_state.compare_right_results = None

    if run_compare:
        if not left_text.strip() or not right_text.strip():
            st.warning("Please fill in both situations before comparing.")
        else:
            with st.spinner("Comparing situations..."):
                st.session_state.compare_left_results = run_pipeline_from_text(left_text.strip())
                st.session_state.compare_right_results = run_pipeline_from_text(right_text.strip())

    st.divider()
    if st.session_state.compare_left_results and st.session_state.compare_right_results:
        lr = st.session_state.compare_left_results
        rr = st.session_state.compare_right_results
        le = lr["extracted"]; re_ = rr["extracted"]

        st.markdown("### Comparison Summary")
        def compare_line(label, lv, rv):
            if lv > rv: return f"- Situation A has more {label}: {lv} vs {rv}"
            if rv > lv: return f"- Situation B has more {label}: {rv} vs {lv}"
            return f"- Both situations have {lv} {label}"
        st.markdown("\n".join([
            compare_line("deadlines", len(le.get("deadlines",[])), len(re_.get("deadlines",[]))),
            compare_line("required documents", len(le.get("requested_documents",[])), len(re_.get("requested_documents",[]))),
            compare_line("action items", len(le.get("action_items",[])), len(re_.get("action_items",[]))),
        ]))
        col1, col2 = st.columns(2)
        with col1:
            render_case_results(lr, "Situation A")
        with col2:
            render_case_results(rr, "Situation B")
    else:
        st.info("Comparison results will appear here.")
