from visaflow.extraction.extractors import extract_deadlines, extract_information


def test_extract_absolute_deadline():
    text = "Please upload both documents by June 3, 2026."
    deadlines = extract_deadlines(text)
    assert "June 3, 2026" in deadlines


def test_extract_relative_deadline():
    text = "Respond to any follow-up requests within 3 business days."
    deadlines = extract_deadlines(text)
    assert "within 3 business days" in deadlines


def test_extract_information():
    text = """
    Please submit the following required documents by June 7, 2026.

    - signed housing agreement
    - proof of enrollment

    After submitting these materials, check the housing portal for updates
    and respond to any follow-up requests within 3 business days.
    """
    extracted = extract_information(text)
    assert "June 7, 2026" in extracted["deadlines"]
    assert "signed housing agreement" in extracted["requested_documents"]
    assert "proof of enrollment" in extracted["requested_documents"]
