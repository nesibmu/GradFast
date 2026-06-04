from visaflow.ingestion.loaders import normalize_text


def test_normalize_text_collapses_spacing():
    raw = "Hello   Nesib,\r\n\r\n\r\nPlease upload   the form.\r\n"
    cleaned = normalize_text(raw)
    assert "Hello Nesib," in cleaned
    assert "\r" not in cleaned
    assert "upload the form." in cleaned
