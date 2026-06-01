from dataclasses import dataclass, field
from typing import List


@dataclass
class Document:
    path: str
    document_type: str
    text: str
    sections: List[str] = field(default_factory=list)


@dataclass
class PlannedTask:
    task: str
    priority: str = "medium"
    source: str = ""
    depends_on: List[str] = field(default_factory=list)


@dataclass
class Plan:
    tasks: List[PlannedTask] = field(default_factory=list)
