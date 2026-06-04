import re
from typing import Dict, List

MONTH_PATTERN = r"(January|February|March|April|May|June|July|August|September|October|November|December)"
DATE_PATTERN = rf"{MONTH_PATTERN}\s+\d{{1,2}}(?:,\s+\d{{4}})?"

ABSOLUTE_DEADLINE_PATTERNS = [
    rf"\bby\s+({DATE_PATTERN})",
    rf"\bdue\s+(?:on\s+)?({DATE_PATTERN})",
    rf"\bsubmit(?:ted)?\s+(?:on|by)\s+({DATE_PATTERN})",
    rf"\bbefore\s+({DATE_PATTERN})",
    rf"\bno later than\s+({DATE_PATTERN})",
]

RELATIVE_DEADLINE_PATTERNS = [
    r"\bwithin\s+\d+\s+business\s+days\b",
    r"\bwithin\s+\d+\s+days\b",
    r"\bat least\s+\d+\s+days before\b",
    r"\b60 days before\b",
    r"\b90 days before\b",
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
        (r"\bi-983\b", "I-983 training plan"),
        (r"\bi-765\b", "I-765 application"),
        (r"\bi-129\b", "I-129 petition"),
        (r"\brecent bank statement\b", "bank statement"),
        (r"\bupdated bank statement\b", "bank statement"),
        (r"\bbank statement\b", "bank statement"),
        (r"\bsigned housing agreement\b", "signed housing agreement"),
        (r"\bhousing agreement\b", "housing agreement"),
        (r"\bjob offer letter\b", "job offer letter"),
        (r"\boffer letter\b", "offer letter"),
        (r"\bh-1b approval notice\b", "H-1B approval notice"),
        (r"\bh-1b petition\b", "H-1B petition"),
        (r"\bemployment authorization document\b", "Employment Authorization Document (EAD)"),
        (r"\bead card\b", "Employment Authorization Document (EAD)"),
        (r"\btraining plan\b", "I-983 training plan"),
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
        "january","february","march","april","may","june",
        "july","august","september","october","november","december"
    ]):
        return 0.95
    if "within" in lowered or "at least" in lowered or "days before" in lowered:
        return 0.82
    return 0.70


def score_document_confidence(item: str) -> float:
    lowered = item.lower()
    strong_terms = [
        "passport","i-20","i-983","i-129","i-765","bank statement",
        "agreement","statement of support","enrollment","offer letter",
        "h-1b","ead","approval notice","training plan"
    ]
    if any(term in lowered for term in strong_terms):
        return 0.92
    if len(item.split()) >= 2:
        return 0.80
    return 0.65


def score_action_confidence(item: str) -> float:
    lowered = item.lower()
    if lowered.startswith("please "):
        return 0.92
    if any(w in lowered for w in ["reply","respond","confirm","notify","contact","schedule"]):
        return 0.88
    if any(w in lowered for w in ["upload","submit","apply","file","request"]):
        return 0.90
    return 0.72


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
        r"we .*? need (.+?)(?:\.|\\n)",
        r"we .*? require (.+?)(?:\.|\\n)",
        r"please upload (.+?)(?: by |\.|\\n)",
        r"please submit (.+?)(?: by |\.|\\n)",
        r"documents include (.+?)(?:\.|\\n)",
        r"required documents.*?include (.+?)(?:\.|\\n)",
        r"including (?:your |my )?(.+?)(?:\.|,| and (?:a |an |the )?(?:copy|signed|completed))",
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
        if lowered in {"documents","materials","items","file","record"}:
            continue
        if lowered.startswith("please "):
            continue
        filtered.append(doc)
    return filtered


def extract_action_items(text: str) -> List[str]:
    actions = []
    action_patterns = [
        r"(please submit .+?)(?:\.|\\n)",
        r"(please upload .+?)(?:\.|\\n)",
        r"(please confirm .+?)(?:\.|\\n)",
        r"(please reply .+?)(?:\.|\\n)",
        r"(please contact .+?)(?:\.|\\n)",
        r"(please notify .+?)(?:\.|\\n)",
        r"(reply to this email.+?)(?:\.|\\n)",
        r"(reply to this message.+?)(?:\.|\\n)",
        r"(respond to this message.+?)(?:\.|\\n)",
        r"(let us know .+?)(?:\.|\\n)",
        r"(follow up .+?)(?:\.|\\n)",
        r"(check the .+? portal.+?)(?:\.|\\n)",
        r"(confirm once .+?)(?:\.|\\n)",
        r"(schedule .+? appointment.+?)(?:\.|\\n)",
        r"(file .+? petition.+?)(?:\.|\\n)",
        r"(apply for .+?)(?:\.|\\n)",
        r"(contact your DSO.+?)(?:\.|\\n)",
        r"(request .+? from your DSO.+?)(?:\.|\\n)",
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
        if lowered in {"please upload","please submit","please confirm"}:
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


def evidence_match_score(item: str, chunk: str) -> int:
    item_norm = normalize_for_matching(item)
    chunk_norm = normalize_for_matching(chunk)
    if item_norm == chunk_norm:
        return 100
    score = 0
    if item_norm in chunk_norm:
        score += 50
    item_words = set(item_norm.split())
    chunk_words = set(chunk_norm.split())
    overlap = len(item_words & chunk_words)
    score += overlap * 8
    if len(chunk.split()) <= 18:
        score += 10
    elif len(chunk.split()) <= 30:
        score += 4
    if chunk.lower().startswith("please"):
        score += 3
    return score


def build_evidence_map(text: str, extracted: Dict[str, List[str]]) -> Dict[str, Dict[str, str]]:
    chunks = split_sentences(text)
    evidence = {"deadlines": {}, "requested_documents": {}, "action_items": {}}
    for category, items in extracted.items():
        if category in {"evidence","confidence"}:
            continue
        for item in items:
            scored = []
            for chunk in chunks:
                score = evidence_match_score(item, chunk)
                if score > 0:
                    scored.append((score, chunk))
            if scored:
                scored.sort(key=lambda x: (-x[0], len(x[1])))
                evidence[category][item] = scored[0][1]
    return evidence


def build_confidence_map(extracted: Dict[str, List[str]]) -> Dict[str, Dict[str, float]]:
    confidence = {"deadlines": {}, "requested_documents": {}, "action_items": {}}
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
