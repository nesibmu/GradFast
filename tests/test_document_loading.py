from pathlib import Path

from visaflow.ingestion.loaders import detect_document_type, split_sections, load_document
from visaflow.schemas import Document


def test_detect_document_type_email():
    text = "Subject: Missing Documents\n\nPlease upload your form."
    assert detect_document_type(text) == "email"


def test_detect_document_type_instruction():
    text = "Housing Checklist\n\nPlease submit the following required documents."
    assert detect_document_type(text) == "instruction"


def test_split_sections():
    text = "Section one\n\nSection two\n\nSection three"
    sections = split_sections(text)
    assert sections == ["Section one", "Section two", "Section three"]


def test_load_document():
    doc = load_document(Path("data/samples/housing_checklist.txt"))
    assert isinstance(doc, Document)
    assert doc.document_type == "instruction"
    assert len(doc.sections) >= 2
