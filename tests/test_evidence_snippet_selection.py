from visaflow.extraction.extractors import extract_information


def test_evidence_prefers_tighter_matching_snippet():
    text = """
    Hello Nesib,

    Please upload your passport copy by June 10, 2026 through the student portal.

    This is part of the larger review for your student file and housing record, and we will continue processing after the required materials are received.

    Please confirm once the documents have been uploaded.
    """
    extracted = extract_information(text)
    evidence = extracted["evidence"]

    assert "Please upload your passport copy by June 10, 2026 through the student portal." == evidence["requested_documents"]["passport copy"]
