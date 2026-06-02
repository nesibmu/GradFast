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


def canonicalize_document_name(text: str) -> str:
    lowered = normalize_for_matching(text)

    replacements = [
        (r"\bcopy of (your )?passport\b", "passport copy"),
        (r"\bcurrent passport copy\b", "passport copy"),
        (r"\bpassport copy\b", "passport copy"),
        (r"\bcopy of passport\b", "passport copy"),
        (r"\bcopy of (your )?current i-20\b", "current I-20"),
        (r"\byour current i-20\b", "current I-20"),
        (r"\bcurrent i-20\b", "current I-20"),
        (r"\bi-20\b", "I-20"),
        (r"\brecent bank statement\b", "bank statement"),
        (r"\bupdated bank statement\b", "bank statement"),
        (r"\bbank statement\b", "bank statement"),
        (r"\bsigned housing agreement\b", "signed housing agreement"),
        (r"\bhousing agreement\b", "housing agreement"),
        (r"\bhousing contract request\b", "housing contract request"),
        (r"\bstatement of support\b", "statement of support"),
    ]

    for pattern, replacement in replacements:
        if re.search(pattern, lowered, flags=re.IGNORECASE):
            return replacement

    return text.strip()


def clean_document_phrase(text: str) -> str:
    text = text.strip(" .,:;")
    text = re.sub(r"^(a|an|the|your|their)\s+", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\bthrough the student portal\b", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\bthrough the portal\b", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\bvia the student portal\b", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\bupload\b", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\bsubmit\b", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s+", " ", text).strip(" .,:;")
    text = canonicalize_document_name(text)
    return text


def score_deadline_confidence(item: str) -> float:
    lowered = item.lower()
    if any(month.lower() in lowered for month in [
        "january", "february", "march", "april", "may", "june",
        "july", "august", "september", "october", "november", "december"
    ]):
        return 0.95
    if "within" in lowered:
        return 0.80
    return 0.70


def score_document_confidence(item: str) -> float:
    lowered = item.lower()
    strong_terms = ["passport", "i-20", "bank statement", "agreement", "statement of support", "enrollment"]
    if any(term in lowered for term in strong_terms):
        return 0.90
    if len(item.split()) >= 2:
        return 0.80
    return 0.65


def score_action_confidence(item: str) -> float:
    lowered = item.lower()
    if lowered.startswith("please "):
        return 0.92
    if "reply" in lowered or "respond" in lowered or "confirm" in lowered:
        return 0.88
    if "upload" in lowered or "submit" in lowered:
        return 0.90
    return 0.70


def dedupe_ordered(items: List[str]) -> List[str]:
    seen = set()
    ordered = []
    for item in items:
        key = normalize_for_matching(item)
        if key not in seen:
            seen.add(key)
            ordered.append(item)
    return ordered


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

    return dedupe_ordered(deadlines)


def extract_requested_documents(text: str) -> List[str]:
    documents = []

    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("- "):
            documents.append(clean_document_phrase(stripped[2:]))

    sentence_patterns = [
        r"we .*? need (.+?)(?:\.|\n)",
        r"we .*? require (.+?)(?:\.|\n)",
        r"please upload (.+?)(?: by |\.|\n)",
        r"please submit (.+?)(?: by |\.|\n)",
        r"to complete your .*?, please upload (.+?)(?: by |\.|\n)",
        r"to complete your .*?, please submit (.+?)(?: by |\.|\n)",
    ]

    for pattern in sentence_patterns:
        for match in re.findall(pattern, text, flags=re.IGNORECASE):
            chunk = match.strip()
            parts = re.split(r",| and ", chunk)
            for part in parts:
                cleaned = clean_document_phrase(part)
                if cleaned and len(cleaned) > 2:
                    documents.append(cleaned)

    documents = dedupe_ordered(documents)

    filtered = []
    for doc in documents:
        lowered = doc.lower()
        if lowered in {"documents", "materials", "items", "file", "record"}:
            continue
        if lowered.startswith("please "):
            continue
        filtered.append(doc)

    return filtered


def extract_action_items(text: str) -> List[str]:
    actions = []
    action_patterns = [
        r"(please submit .+?)(?:\.|\n)",
        r"(please upload .+?)(?:\.|\n)",
        r"(please confirm .+?)(?:\.|\n)",
        r"(please reply .+?)(?:\.|\n)",
        r"(reply to this email.+?)(?:\.|\n)",
        r"(reply to this message.+?)(?:\.|\n)",
        r"(respond to this message.+?)(?:\.|\n)",
        r"(respond to any follow-up requests.+?)(?:\.|\n)",
        r"(let us know .+?)(?:\.|\n)",
        r"(follow up .+?)(?:\.|\n)",
        r"(check the .+? portal.+?)(?:\.|\n)",
        r"(upload .+? through the .+? portal.+?)(?:\.|\n)",
        r"(confirm once .+?)(?:\.|\n)",
        r"(if you need an extension, respond .+?)(?:\.|\n)",
        r"(if you expect any delay, reply .+?)(?:\.|\n)",
    ]

    for pattern in action_patterns:
        for match in re.findall(pattern, text, flags=re.IGNORECASE):
            cleaned = re.sub(r"\s+", " ", match).strip(" .")
            if cleaned:
                actions.append(cleaned)

    actions = dedupe_ordered(actions)

    filtered = []
    for action in actions:
        lowered = action.lower()
        if lowered in {"please upload", "please submit", "please confirm"}:
            continue
        filtered.append(action)

    return filtered


def remove_document_action_overlap(documents: List[str], actions: List[str]) -> List[str]:
    filtered_docs = []
    normalized_actions = [normalize_for_matching(a) for a in actions]

    for doc in documents:
        doc_norm = normalize_for_matching(doc)
        overlap = False
        for action_norm in normalized_actions:
            if doc_norm and doc_norm in action_norm and len(doc_norm.split()) >= 3:
                overlap = True
                break
        if not overlap:
            filtered_docs.append(doc)

    return filtered_docs


def build_evidence_map(text: str, extracted: Dict[str, List[str]]) -> Dict[str, Dict[str, str]]:
    chunks = split_sentences(text)
    normalized_chunks = [(chunk, normalize_for_matching(chunk)) for chunk in chunks]

    evidence = {
        "deadlines": {},
        "requested_documents": {},
        "action_items": {},
    }

    for category, items in extracted.items():
        if category in {"evidence", "confidence"}:
            continue

        for item in items:
            normalized_item = normalize_for_matching(item)

            for original_chunk, normalized_chunk in normalized_chunks:
                if normalized_item in normalized_chunk:
                    evidence[category][item] = original_chunk
                    break

    return evidence


def build_confidence_map(extracted: Dict[str, List[str]]) -> Dict[str, Dict[str, float]]:
    confidence = {
        "deadlines": {},
        "requested_documents": {},
        "action_items": {},
    }

    for item in extracted.get("deadlines", []):
        confidence["deadlines"][item] = score_deadline_confidence(item)

    for item in extracted.get("requested_documents", []):
        confidence["requested_documents"][item] = score_document_confidence(item)

    for item in extracted.get("action_items", []):
        confidence["action_items"][item] = score_action_confidence(item)

    return confidence


def extract_information(text: str) -> Dict[str, object]:
    deadlines = extract_deadlines(text)
    documents = extract_requested_documents(text)
    actions = extract_action_items(text)
    documents = remove_document_action_overlap(documents, actions)

    extracted = {
        "deadlines": deadlines,
        "requested_documents": documents,
        "action_items": actions,
    }
    extracted["evidence"] = build_evidence_map(text, extracted)
    extracted["confidence"] = build_confidence_map(extracted)
    return extracted
