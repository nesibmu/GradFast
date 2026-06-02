import streamlit as st

from visaflow.config import SAMPLES_DIR
from visaflow.ingestion.loaders import load_document
from visaflow.extraction.extractors import extract_information
from visaflow.planning.planner import build_task_plan
from visaflow.drafting.drafter import draft_response_with_mode, generate_next_step_summary


def run_pipeline_from_text(text: str, enhanced_draft: bool):
    extracted = extract_information(text)
    plan = build_task_plan(extracted)
    draft = draft_response_with_mode(plan, enhanced=enhanced_draft)
    summary = generate_next_step_summary(plan)
    return extracted, plan, summary, draft


def priority_emoji(priority: str) -> str:
    if priority == "high":
        return "🔴"
    if priority == "medium":
        return "🟡"
    return "⚪"


st.set_page_config(page_title="VisaFlow", layout="wide")

st.title("VisaFlow")
st.caption("AI operations agent for international-student bureaucracy")

sample_files = sorted([p.name for p in SAMPLES_DIR.glob("*.txt")])

with st.sidebar:
    st.header("Demo Controls")
    input_mode = st.radio("Input mode", ["Sample file", "Paste text"])
    enhanced_draft = st.checkbox("Use enhanced draft mode", value=True)

    selected_file = None
    pasted_text = ""

    if input_mode == "Sample file":
        selected_file = st.selectbox("Choose a sample file", sample_files)
    else:
        pasted_text = st.text_area(
            "Paste email or document text",
            height=250,
            placeholder="Paste an administrative email or document here...",
        )

    run_pipeline = st.button("Run pipeline")

if run_pipeline:
    if input_mode == "Sample file":
        document = load_document(SAMPLES_DIR / selected_file)
        source_text = document.text
    else:
        source_text = pasted_text.strip()

    if not source_text:
        st.warning("Please provide some input text first.")
    else:
        extracted, plan, summary, draft = run_pipeline_from_text(source_text, enhanced_draft)

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

        if plan.tasks:
            grouped = {}
            for task in plan.tasks:
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
            st.write("No tasks generated.")

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
        st.text_area("Draft", draft, height=240)
else:
    st.info("Choose a sample file or paste text, then click 'Run pipeline'.")
