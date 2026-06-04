from visaflow.extraction.extractors import extract_action_items


def test_extract_submit_and_confirm_actions():
    text = """
    Please submit your updated housing contract request and a recent bank statement by May 28, 2026.
    Please confirm once the materials have been uploaded.
    """
    actions = extract_action_items(text)
    assert any("please submit" in action.lower() for action in actions)
    assert any("please confirm" in action.lower() for action in actions)


def test_extract_portal_and_followup_actions():
    text = """
    You should also upload a copy of your passport and current I-20 through the student portal.
    Respond to any follow-up requests within 3 business days.
    """
    actions = extract_action_items(text)
    assert any("upload" in action.lower() for action in actions)
    assert any("respond to any follow-up requests" in action.lower() for action in actions)
