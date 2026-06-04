from pathlib import Path
import os

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
SAMPLES_DIR = DATA_DIR / "samples"

SUPPORTED_EXTENSIONS = {".txt", ".md"}
DEFAULT_CONFIDENCE = 0.75

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini")

APP_TITLE = "VisaFlow"
APP_SUBTITLE = "AI Career & Visa Copilot for International Students"

DEMO_PRESETS = {
    "OPT STEM Extension Filing": {
        "file": "opt_situation.txt",
        "note": "F-1 student preparing STEM OPT extension and H-1B transition — extracts deadlines, required documents, and action plan.",
    },
    "Job Search Strategy": {
        "file": "job_search_question.txt",
        "note": "International student building H-1B-friendly job search — generates prioritized strategy and interview prep.",
    },
    "Cap-Gap Protection": {
        "file": "cap_gap_question.txt",
        "note": "Student navigating the OPT-to-H-1B gap period — extracts risks, deadlines, and required DSO actions.",
    },
    "Housing Email (Legacy)": {
        "file": "housing_email.txt",
        "note": "Original demo: administrative housing email workflow.",
    },
    "Financial Aid (Legacy)": {
        "file": "financial_aid_email.txt",
        "note": "Original demo: financial aid email workflow.",
    },
}
