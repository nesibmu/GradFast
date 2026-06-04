from visaflow.ingestion.loaders import load_document
from visaflow.extraction.extractors import extract_information
from visaflow.planning.planner import build_task_plan
from visaflow.drafting.drafter import draft_response_with_mode
from visaflow.utils.render import render_result
from visaflow.config import SAMPLES_DIR


def run_demo(filename: str, enhanced_draft: bool = False) -> str:
    document = load_document(SAMPLES_DIR / filename)
    extracted = extract_information(document.text)
    plan = build_task_plan(extracted)
    response = draft_response_with_mode(plan, enhanced=enhanced_draft)
    return render_result(document.text, extracted, plan, response)


if __name__ == "__main__":
    print(run_demo("housing_email.txt"))
