import re
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
from pypdf import PdfReader

STOP = set(ENGLISH_STOP_WORDS)

SKILLS = [
    "python", "sql", "excel", "tableau", "power bi", "java", "javascript", "c++",
    "html", "css", "react", "aws", "azure", "docker", "git", "linux",
    "machine learning", "deep learning", "statistics", "data analysis",
    "sap", "autocad", "quickbooks", "accounting", "payroll", "recruiting",
    "sales", "marketing", "seo", "customer service", "project management",
    "leadership", "communication", "negotiation", "budgeting", "auditing",
    "teaching", "training", "nursing", "patient care", "cpr", "fitness",
    "agile", "scrum", "jira", "salesforce", "photoshop", "illustrator",
]

def clean(text):
    text = str(text).lower()
    text = re.sub(r"http\S+|www\S+", " ", text)
    text = re.sub(r"[^a-z0-9\s+#.]", " ", text)
    words = [w.strip(".") for w in text.split()]
    return " ".join(w for w in words if w and w not in STOP)

def extract_skills(clean_text):
    found = []
    for s in SKILLS:
        if re.search(r"(?<![a-z0-9])" + re.escape(s) + r"(?![a-z0-9])", clean_text):
            found.append(s)
    return found

def read_file(f):
    """Read a Streamlit UploadedFile (pdf or txt) into a string."""
    if f.name.lower().endswith(".pdf"):
        reader = PdfReader(f)
        return " ".join((p.extract_text() or "") for p in reader.pages)
    return f.read().decode("utf-8", errors="ignore")
