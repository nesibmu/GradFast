from visaflow.extraction.extractors import extract_requested_documents


def test_extract_requested_documents_from_mixed_list_sentence():
    text = """
    To complete your file, please upload your signed housing agreement, a recent bank statement, a copy of your passport, and your current I-20 by June 15, 2026 through the student portal.
    """
    docs = extract_requested_documents(text)

    assert "signed housing agreement" in docs
    assert "recent bank statement" in docs
    assert "copy of your passport" in docs or "copy of passport" in docs
    assert "current I-20" in docs or "I-20" in docs
