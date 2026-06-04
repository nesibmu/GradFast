from visaflow.extraction.extractors import run_extraction
from visaflow.planning.planner import build_plan


def test_pipeline_finds_deadline_and_documents():
    text = "Please submit your passport and bank statement by May 28, 2026."
    result = run_extraction(text)
    assert result.deadlines
    assert any(doc.name == "Passport" for doc in result.documents)
    assert any(doc.name == "Bank Statement" for doc in result.documents)

    plan = build_plan(result)
    assert plan.tasks
