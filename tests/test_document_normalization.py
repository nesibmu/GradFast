from visaflow.extraction.extractors import extract_requested_documents


def test_document_variants_are_normalized():
    text = """
    Please upload a copy of your passport, your current passport copy, and your recent bank statement by June 10, 2026.
    """
    docs = extract_requested_documents(text)

    assert "passport copy" in docs
    assert "bank statement" in docs
    assert len([d for d in docs if d == "passport copy"]) == 1
