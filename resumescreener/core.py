import re
from pathlib import Path
import joblib
import streamlit as st
from sklearn.metrics.pairwise import cosine_similarity
from utils import clean, extract_skills, extract_contact

BASE = Path(__file__).parent
SIM_CAP = 0.30
VERBS = {"led", "built", "developed", "managed", "designed", "created", "improved",
         "increased", "reduced", "launched", "implemented", "analyzed", "delivered",
         "automated", "optimized", "organized", "trained", "negotiated", "achieved",
         "coordinated", "supervised", "streamlined"}


@st.cache_resource
def load_models():
    return (joblib.load(BASE / "artifacts" / "tfidf.pkl"),
            joblib.load(BASE / "artifacts" / "clf.pkl"))


def require(role=None):
    """Stop the page unless the user is logged in (with the right role)."""
    u = st.session_state.get("user")
    if not u:
        st.warning("Please log in on the Home page first.")
        st.stop()
    if role and u["role"] != role:
        st.error(f"This page is only for {role}s.")
        st.stop()
    return u


def match(resume, jd, must):
    """Match score (0-100) between a resume and a job."""
    tfidf, _ = load_models()
    rc, jc = clean(resume), clean(jd)
    sim = cosine_similarity(tfidf.transform([jc]), tfidf.transform([rc]))[0, 0]
    text = float(min(sim / SIM_CAP, 1.0))
    found = set(extract_skills(rc))
    matched = [s for s in must if s in found]
    missing = [s for s in must if s not in found]
    if must:
        score = 100 * (0.5 * text + 0.5 * len(matched) / len(must))
    else:
        score = 100 * text
    return {"score": round(score, 1), "text": round(100 * text, 1),
            "matched": matched, "missing": missing}


def ats_report(resume, jd="", must=None):
    """ATS score out of 100: job match (60) + structure (25) + content (15)."""
    must = must or []
    low = resume.lower()
    words = re.findall(r"[a-z']+", low)
    email, phone = extract_contact(resume)
    checks = []

    def add(group, label, ok, pts, tip):
        checks.append({"group": group, "label": label, "ok": bool(ok), "pts": pts, "tip": tip})

    add("Structure", "Email and phone present", email and phone, 5,
        "Add a professional email and phone number at the top.")
    add("Structure", "Summary / objective section",
        re.search(r"\b(summary|objective|profile)\b", low), 5,
        "Add a 2-3 line professional summary.")
    add("Structure", "Work experience section",
        re.search(r"\b(experience|employment|work history|internship)\b", low), 5,
        "Add a clearly labeled Work Experience section.")
    add("Structure", "Education section",
        re.search(r"\b(education|university|college|b\.?tech|b\.?sc|bachelor|master|diploma)\b", low), 5,
        "Add an Education section with degree and year.")
    add("Structure", "Skills section", re.search(r"\bskills?\b", low), 5,
        "Add a Skills section listing tools and technologies.")
    add("Content", "Length of 200 to 1000 words", 200 <= len(words) <= 1000, 5,
        f"Your resume has {len(words)} words. Aim for 1-2 pages (200 to 1000 words).")
    used = VERBS & set(words)
    add("Content", "Uses strong action verbs (5 or more)", len(used) >= 5, 5,
        "Start bullet points with verbs such as built, led, improved, automated.")
    metrics = re.findall(r"\d+\s?%|[$₹]\s?\d|\b\d+\s?(?:k|m|lakh|crore|users|clients|projects)\b", low)
    add("Content", "Measurable results (3 or more numbers)", len(metrics) >= 3, 5,
        "Quantify achievements, e.g. 'reduced report time by 30%'.")

    earned = sum(c["pts"] for c in checks if c["ok"])
    possible = sum(c["pts"] for c in checks)
    result = {"checks": checks, "matched": [], "missing": [], "match": None}

    if jd.strip():
        m = match(resume, jd, must)
        result["match"] = m
        result["matched"], result["missing"] = m["matched"], m["missing"]
        total = 60 * m["score"] / 100 + earned
        possible += 60
    else:
        total = earned
    result["score"] = round(100 * total / possible, 1)
    return result
