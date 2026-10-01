import re
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
from pypdf import PdfReader

STOP = set(ENGLISH_STOP_WORDS)

_SKILLS = {
    "python": [], "sql": [], "mysql": [], "postgresql": ["postgres"], "mongodb": [],
    "excel": [], "tableau": [], "power bi": ["powerbi"], "java": [], "javascript": ["js"],
    "typescript": [], "c++": [], "c#": [], "php": [], "ruby": [], "html": [], "css": [],
    "react": [], "angular": [], "node.js": ["nodejs", "node js"], "django": [], "flask": [],
    "aws": [], "azure": [], "gcp": [], "docker": [], "kubernetes": [], "git": [],
    "linux": [], "ci cd": [], "jenkins": [], "api": ["apis", "rest api"],
    "machine learning": ["ml"], "deep learning": [], "natural language processing": ["nlp"],
    "data analysis": [], "data science": [], "data visualization": [], "statistics": [],
    "pandas": [], "numpy": [], "tensorflow": [], "pytorch": [], "spark": [], "hadoop": [],
    "etl": [], "cybersecurity": [], "networking": [], "testing": ["qa"], "agile": [],
    "scrum": [], "jira": [],
    "accounting": [], "auditing": [], "budgeting": [], "financial analysis": [],
    "quickbooks": [], "sap": [], "tally": [], "payroll": [], "recruiting": ["recruitment"],
    "talent acquisition": [], "employee relations": [], "onboarding": [],
    "sales": [], "marketing": [], "seo": [], "social media": [], "salesforce": [],
    "crm": [], "negotiation": [], "customer service": [], "project management": [],
    "product management": [], "business development": [], "supply chain": [],
    "logistics": [], "procurement": [],
    "leadership": [], "communication": [], "teamwork": [], "problem solving": [],
    "time management": [], "presentation": [], "training": [], "teaching": [],
    "nursing": [], "patient care": [], "cpr": [], "fitness": [], "autocad": [],
    "photoshop": [], "illustrator": [], "figma": [], "video editing": [],
    "cooking": [], "food safety": [],
}
SKILLS = sorted(_SKILLS)

def _pat(term):
    return re.compile(r"(?<![a-z0-9])" + re.escape(term) + r"(?![a-z0-9])")

_SKILL_RE = {s: [_pat(t) for t in [s] + al] for s, al in _SKILLS.items()}

EDU_LEVELS = {0: "Not found", 1: "Diploma", 2: "Bachelor's", 3: "Master's", 4: "PhD"}
_EDU_TERMS = {
    4: ["phd", "ph.d", "doctorate", "doctoral"],
    3: ["masters", "master of", "msc", "m.sc", "mba", "m.tech", "mtech", "mca"],
    2: ["bachelor", "bachelors", "b.sc", "bsc", "b.tech", "btech", "bba", "bca",
        "b.com", "bcom", "b.e", "b.a"],
    1: ["diploma", "associate degree"],
}
_EDU_RE = {lvl: [re.compile(r"(?<![a-z0-9])" + re.escape(t) + r"(?![a-z])") for t in ts]
           for lvl, ts in _EDU_TERMS.items()}

EMAIL_RE = re.compile(r"[\w.\-+]+@[\w\-]+\.[\w.\-]+")
PHONE_RE = re.compile(r"\+?\d[\d\s\-()]{8,16}\d")
YEARS_RE = re.compile(r"(\d{1,2})\s*\+?\s*(?:years|year|yrs|yr)\b")


def clean(text):
    text = str(text).lower()
    text = re.sub(r"http\S+|www\S+", " ", text)
    text = re.sub(r"[^a-z0-9\s+#.]", " ", text)
    words = [w.strip(".") for w in text.split()]
    return " ".join(w for w in words if w and w not in STOP)


def extract_skills(clean_text):
    return [s for s, pats in _SKILL_RE.items() if any(p.search(clean_text) for p in pats)]


def extract_years(text):
    vals = [int(v) for v in YEARS_RE.findall(str(text).lower())]
    vals = [v for v in vals if 0 < v <= 40]
    return max(vals) if vals else 0


def extract_education(clean_text):
    for lvl in (4, 3, 2, 1):
        if any(p.search(clean_text) for p in _EDU_RE[lvl]):
            return EDU_LEVELS[lvl], lvl
    return EDU_LEVELS[0], 0


def extract_contact(raw_text):
    m = EMAIL_RE.search(raw_text)
    email = m.group(0).rstrip(".") if m else ""
    phone = ""
    for p in PHONE_RE.finditer(raw_text):
        s = p.group(0).strip()
        digits = re.sub(r"\D", "", s)
        if 10 <= len(digits) <= 13 and not re.fullmatch(r"(?:(?:19|20)\d{2}\D*)+", s):
            phone = s
            break
    return email, phone


def read_file(f):
    """Read a Streamlit UploadedFile (pdf, docx or txt) into a string."""
    name = f.name.lower()
    if name.endswith(".pdf"):
        reader = PdfReader(f)
        return " ".join((p.extract_text() or "") for p in reader.pages)
    if name.endswith(".docx"):
        from docx import Document
        return "\n".join(p.text for p in Document(f).paragraphs)
    return f.read().decode("utf-8", errors="ignore")
