from visaflow.extraction.extractors import split_sentences, extract_information


def test_split_sentences_handles_blank_lines_and_periods():
    text = """
    Hello Nesib,

    Please upload your passport by June 12, 2026.

    Please confirm once the materials have been uploaded.
    """
    chunks = split_sentences(text)

    assert any("Please upload your passport by June 12, 2026." in chunk for chunk in chunks)
    assert any("Please confirm once the materials have been uploaded." in chunk for chunk in chunks)


def test_evidence_map_matches_cleaner_snippets():
    text = """
    Hello Nesib,

    Please upload your passport by June 12, 2026.

    Please confirm once the materials have been uploaded.
    """
    extracted = extract_information(text)
    evidence = extracted["evidence"]

    assert evidence["deadlines"]["June 12, 2026"] == "Please upload your passport by June 12, 2026."
    assert any(
        "please confirm once the materials have been uploaded" in action.lower()
        for action in extracted["action_items"]
    )
