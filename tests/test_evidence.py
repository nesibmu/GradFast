from visaflow.extraction.extractors import extract_information


def test_evidence_map_contains_deadline_sentence():
    text = """
    Please upload both documents by June 3, 2026.
    Please confirm once the materials have been uploaded.
    """
    extracted = extract_information(text)
    evidence = extracted["evidence"]

    assert "June 3, 2026" in evidence["deadlines"]
    assert "Please upload both documents by June 3, 2026." == evidence["deadlines"]["June 3, 2026"]


def test_evidence_map_contains_action_sentence():
    text = """
    Please confirm once the materials have been uploaded.
    """
    extracted = extract_information(text)
    evidence = extracted["evidence"]

    action = extracted["action_items"][0]
    assert action in evidence["action_items"]
