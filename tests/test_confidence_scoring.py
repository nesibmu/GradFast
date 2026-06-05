from visaflow.extraction.extractors import extract_information


def test_confidence_scores_are_attached():
    text = """
    Please upload your passport by June 12, 2026.
    Please confirm once the materials have been uploaded.
    """
    extracted = extract_information(text)

    assert "confidence" in extracted
    assert "June 12, 2026" in extracted["confidence"]["deadlines"]

    action_items = extracted["action_items"]
    assert len(action_items) >= 1
    assert action_items[0] in extracted["confidence"]["action_items"]


def test_deadline_confidence_is_high_for_absolute_dates():
    text = "Please upload your passport by June 12, 2026."
    extracted = extract_information(text)

    assert extracted["confidence"]["deadlines"]["June 12, 2026"] >= 0.9
