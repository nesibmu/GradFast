from visaflow.extraction.extractors import extract_action_items


def test_extract_action_item_variants():
    text = """
    Please confirm once the documents have been uploaded.
    If you expect any delay, reply to this message as soon as possible.
    Let us know if anything in the request is unclear.
    """
    actions = extract_action_items(text)

    assert any("please confirm once the documents have been uploaded" in a.lower() for a in actions)
    assert any("reply to this message as soon as possible" in a.lower() for a in actions)
    assert any("let us know if anything in the request is unclear" in a.lower() for a in actions)
