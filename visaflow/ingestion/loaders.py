from pathlib import Path
from typing import List
import re

from visaflow.schemas import Document


def normalize_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n\n", text)
    return text.strip()


def detect_document_type(text: str) -> str:
    lowered = text.lower()
    if "subject:" in lowered or "from:" in lowered:
        return "email"
    if "please submit" in lowered or "required documents" in lowered or "application" in lowered:
        return "instruction"
    return "generic"


def split_sections(text: str) -> List[str]:
    parts = re.split(r"\n\n+", text)
    return [part.strip() for part in parts if part.strip()]


def load_text_file(path: Path, normalize: bool = True) -> str:
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    return normalize_text(text) if normalize else text


def load_document(path: Path) -> Document:
    text = load_text_file(path)
    return Document(
        path=str(path),
        document_type=detect_document_type(text),
        text=text,
        sections=split_sections(text),
    )


def load_sample_documents(directory: Path) -> List[Document]:
    documents = []
    for path in sorted(directory.glob("*.txt")):
        documents.append(load_document(path))
    return documents
