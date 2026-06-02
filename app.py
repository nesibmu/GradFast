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
}


def run_pipeline_from_text(text: str):
    extracted = extract_information(text)
    plan = build_task_plan(extracted)
    summary = generate_next_step_summary(plan)
    baseline_draft = draft_response_with_mode(plan, enhanced=False)
    enhanced_draft = draft_response_with_mode(plan, enhanced=True)
    return extracted, plan, summary, baseline_draft, enhanced_draft


def priority_emoji(priority: str) -> str:
    if priority == "high":
        return "🔴"
    if priority == "medium":
        return "🟡"
    return "⚪"


st.set_page_config(page_title="VisaFlow", layout="wide")

st.title("VisaFlow")
st.caption("AI operations agent for international-student bureaucracy")

st.markdown(
    """
VisaFlow helps turn messy administrative emails and document requests into:
1. structured extracted information,
2. a prioritized task plan,
3. a ready-to-edit draft response.
"""
)

with st.expander("Demo guide", expanded=True):
    st.write("Recommended flow for the demo:")
    st.write("1. Start with a preset to show a fast end-to-end example.")
    st.write("2. Show extracted deadlines, documents, and action items.")
    st.write("3. Show the task plan, filtering, and evidence.")
    st.write("4. Compare baseline vs enhanced draft output.")
    st.write("5. End with pasted text or uploaded file input.")

    st.write("")
    st.write("Preset guide:")
    for name, preset in DEMO_PRESETS.items():
        st.write(f"- **{name}**: {preset['description']}")

sample_files = sorted([p.name for p in SAMPLES_DIR.glob("*.txt")])

with st.sidebar:
    st.header("Demo Controls")
    input_mode = st.radio(
        "Input mode",
        ["Demo preset", "Sample file", "Paste text", "Upload file"]
    )
    show_comparison = st.checkbox("Show baseline vs enhanced draft", value=True)

    selected_preset = None
    selected_file = None
    pasted_text = ""
    uploaded_file = None

    if input_mode == "Demo preset":
        selected_preset = st.selectbox("Choose a demo preset", list(DEMO_PRESETS.keys()))
        st.caption(DEMO_PRESETS[selected_preset]["description"])
    elif input_mode == "Sample file":
        selected_file = st.selectbox("Choose a sample file", sample_files)
    elif input_mode == "Paste text":
        pasted_text = st.text_area(
            "Paste email or document text",
            height=250,
            placeholder="Paste an administrative email or document here...",
        )
    else:
        uploaded_file = st.file_uploader("Upload a .txt file", type=["txt"])

    run_pipeline = st.button("Run pipeline")

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
        st.warning("Please provide some input text first.")
    else:
        extracted, plan, summary, baseline_draft, enhanced_draft = run_pipeline_from_text(source_text)

        deadlines = extracted.get("deadlines", [])
        documents = extracted.get("requested_documents", [])
        actions = extracted.get("action_items", [])

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Deadlines", len(deadlines))
        m2.metric("Documents", len(documents))
        m3.metric("Actions", len(actions))
        m4.metric("Planned Tasks", len(plan.tasks))

        st.divider()

        left, right = st.columns([1.2, 1])

        with left:
            st.subheader("Source")
            st.text_area("Input text", source_text, height=320)

        with right:
            st.subheader("Next-Step Summary")
            st.text_area("Summary", summary, height=320)

        st.divider()

        col1, col2, col3 = st.columns(3)

        with col1:
            st.subheader("Deadlines")
            if deadlines:
                for item in deadlines:
                    st.write(f"- {item}")
            else:
                st.write("None found.")

        with col2:
            st.subheader("Requested Documents")
            if documents:
                for item in documents:
                    st.write(f"- {item}")
            else:
                st.write("None found.")

        with col3:
            st.subheader("Action Items")
            if actions:
                for item in actions:
                    st.write(f"- {item}")
            else:
                st.write("None found.")

        st.divider()

        st.subheader("Planned Tasks")

        workflow_options = ["all"] + sorted({task.workflow_type for task in plan.tasks})
        priority_options = ["all", "high", "medium", "low"]

        f1, f2 = st.columns(2)
        with f1:
            selected_workflow = st.selectbox("Filter by workflow", workflow_options)
        with f2:
            selected_priority = st.selectbox("Filter by priority", priority_options)

        filtered_tasks = []
        for task in plan.tasks:
            workflow_ok = selected_workflow == "all" or task.workflow_type == selected_workflow
            priority_ok = selected_priority == "all" or task.priority == selected_priority
            if workflow_ok and priority_ok:
                filtered_tasks.append(task)

        if filtered_tasks:
            grouped = {}
            for task in filtered_tasks:
                grouped.setdefault(task.workflow_type, []).append(task)

            for workflow_type, tasks in grouped.items():
                st.markdown(f"**{workflow_type.replace('_', ' ').title()}**")
                for task in tasks:
                    dep_text = ""
                    if task.depends_on:
                        dep_text = f"  \nDepends on: {', '.join(task.depends_on)}"
                    st.markdown(
                        f"{priority_emoji(task.priority)} **{task.task}**  \n"
                        f"Priority: `{task.priority}` | Source: `{task.source}`{dep_text}"
                    )
                st.write("")
        else:
            st.write("No tasks match the selected filters.")

        evidence = extracted.get("evidence", {})
        if evidence:
            st.divider()
            st.subheader("Evidence")
            for category in ["deadlines", "requested_documents", "action_items"]:
                category_evidence = evidence.get(category, {})
                if category_evidence:
                    with st.expander(category.replace("_", " ").title(), expanded=False):
                        for item, snippet in category_evidence.items():
                            st.write(f"**{item}**")
                            st.caption(snippet)

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
                )
        else:
            editable_draft = st.text_area("Editable draft", enhanced_draft, height=260)
            st.download_button(
                label="Download draft as .txt",
                data=editable_draft,
                file_name="visaflow_draft.txt",
                mime="text/plain",
            )
else:
    st.info("Choose a preset, sample file, pasted text, or uploaded file, then click 'Run pipeline'.")
