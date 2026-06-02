from visaflow.extraction.extractors import extract_information


def test_document_action_overlap_is_reduced():
    text = """
    Please upload your signed housing agreement through the student portal by June 15, 2026.
    Please confirm once the documents have been uploaded.
    """
    extracted = extract_information(text)

    docs = extracted["requested_documents"]
    actions = extracted["action_items"]

    assert any("please confirm" in a.lower() for a in actions)
    assert len(set(a.lower() for a in actions)) == len(actions)
    assert len(set(d.lower() for d in docs)) == len(docs)
