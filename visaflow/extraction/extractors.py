import re
from typing import Dict, List


MONTH_PATTERN = r"(January|February|March|April|May|June|July|August|September|October|November|December)"
DATE_PATTERN = rf"{MONTH_PATTERN}\s+\d{{1,2}}(?:,\s+\d{{4}})?"

ABSOLUTE_DEADLINE_PATTERNS = [
    rf"\bby\s+({DATE_PATTERN})",
    rf"\bdue\s+(?:on\s+)?({DATE_PATTERN})",
    rf"\bsubmit(?:ted)?\s+(?:on|by)\s+({DATE_PATTERN})",
]

RELATIVE_DEADLINE_PATTERNS = [
    r"\bwithin\s+\d+\s+business\s+days\b",
    r"\bwithin\s+\d+\s+days\b",
]


def normalize_for_matching(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"\s+", " ", text)
    return text


def split_sentences(text: str) -> List[str]:
    text = text.replace("\r\n", "\n").replace("\r", "\n").strip()

    raw_chunks = re.split(r"\n\s*\n|(?<=[.!?])\s+(?=[A-Z])", text)
    cleaned = []

    for chunk in raw_chunks:
        chunk = re.sub(r"\s+", " ", chunk).strip()
        if chunk:
            cleaned.append(chunk)

    return cleaned


def extract_deadlines(text: str) -> List[str]:
    deadlines = []

    for pattern in ABSOLUTE_DEADLINE_PATTERNS:
        for match in re.findall(pattern, text, flags=re.IGNORECASE):
            if isinstance(match, tuple):
                match = match[0]
            deadlines.append(match.strip())

    for pattern in RELATIVE_DEADLINE_PATTERNS:
        for match in re.findall(pattern, text, flags=re.IGNORECASE):
            deadlines.append(match.strip())

    seen = set()
    ordered = []
    for item in deadlines:
        key = normalize_for_matching(item)
        if key not in seen:
            seen.add(key)
            ordered.append(item)

    return ordered


def extract_requested_documents(text: str) -> List[str]:
    documents = []

    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("- "):
            documents.append(stripped[2:].strip())

    sentence_patterns = [
        r"we .*? need (.+?)(?:\.|\n)",
        r"we .*? require (.+?)(?:\.|\n)",
        r"please upload (.+?)(?:\.|\n)",
        r"please submit (.+?)(?:\.|\n)",
    ]

    for pattern in sentence_patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            chunk = match.group(1)
            parts = re.split(r",| and ", chunk)
            for part in parts:
                cleaned = part.strip(" .")
                if cleaned and len(cleaned) > 2:
                    documents.append(cleaned)

    seen = set()
    ordered = []
    for item in documents:
        key = normalize_for_matching(item)
        if key not in seen:
            seen.add(key)
            ordered.append(item)

    return ordered


def extract_action_items(text: str) -> List[str]:
    actions = []
    sentence_patterns = [
        r"(please submit .+?)(?:\.|\n)",
        r"(please upload .+?)(?:\.|\n)",
        r"(please confirm .+?)(?:\.|\n)",
        r"(reply to this email.+?)(?:\.|\n)",
        r"(respond to this message.+?)(?:\.|\n)",
        r"(respond to any follow-up requests.+?)(?:\.|\n)",
        r"(check the .+? portal.+?)(?:\.|\n)",
        r"(upload .+? through the .+? portal.+?)(?:\.|\n)",
    ]

    for pattern in sentence_patterns:
        for match in re.findall(pattern, text, flags=re.IGNORECASE):
            cleaned = match.strip(" .")
            if cleaned:
                actions.append(cleaned)

    seen = set()
    ordered = []
    for item in actions:
        key = normalize_for_matching(item)
        if key not in seen:
            seen.add(key)
            ordered.append(item)

    return ordered


def build_evidence_map(text: str, extracted: Dict[str, List[str]]) -> Dict[str, Dict[str, str]]:
    chunks = split_sentences(text)
    normalized_chunks = [(chunk, normalize_for_matching(chunk)) for chunk in chunks]

    evidence = {
        "deadlines": {},
        "requested_documents": {},
        "action_items": {},
    }

    for category, items in extracted.items():
        if category == "evidence":
            continue

        for item in items:
            normalized_item = normalize_for_matching(item)

            for original_chunk, normalized_chunk in normalized_chunks:
                if normalized_item in normalized_chunk:
                    evidence[category][item] = original_chunk
                    break

    return evidence


def extract_information(text: str) -> Dict[str, object]:
    extracted = {
        "deadlines": extract_deadlines(text),
        "requested_documents": extract_requested_documents(text),
        "action_items": extract_action_items(text),
    }
    extracted["evidence"] = build_evidence_map(text, extracted)
    return extracted
