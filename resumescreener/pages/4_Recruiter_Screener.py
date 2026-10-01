import json
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
import streamlit as st
from sklearn.metrics.pairwise import cosine_similarity
from utils import clean, extract_skills, read_file, SKILLS
from core import require

require("recruiter")

BASE = Path(__file__).resolve().parents[1]


@st.cache_resource
def load_artifacts():
    tfidf = joblib.load(BASE / "artifacts" / "tfidf.pkl")
    clf = joblib.load(BASE / "artifacts" / "clf.pkl")
    db = pd.read_csv(BASE / "artifacts" / "resumes_db.csv")
    db["clean"] = db["clean"].fillna("")
    db["preview"] = db["preview"].fillna("")
    metrics = json.load(open(BASE / "artifacts" / "metrics.json"))
    db_vecs = tfidf.transform(db["clean"])
    return tfidf, clf, db, db_vecs, metrics


tfidf, clf, db, db_vecs, metrics = load_artifacts()


def rank(jd, cleaned_texts, required, w_text):
    jd_vec = tfidf.transform([clean(jd)])
    vecs = tfidf.transform(cleaned_texts)
    sim = cosine_similarity(jd_vec, vecs).flatten()
    matched, pct = [], []
    for t in cleaned_texts:
        found = extract_skills(t)
        m = [s for s in required if s in found]
        matched.append(m)
        pct.append(len(m) / len(required) if required else 0.0)
    pct = np.array(pct)
    final = w_text * sim + (1 - w_text) * pct
    return sim, pct, final, matched, vecs


st.sidebar.title("⚙️ Settings")
w_text = st.sidebar.slider("Weight: text similarity vs skill match", 0.0, 1.0, 0.6, 0.05,
                           help="1.0 = only text similarity, 0.0 = only skill match")
top_n = st.sidebar.number_input("Shortlist size", 1, 50, 10)
min_score = st.sidebar.slider("Minimum final score (%)", 0, 100, 0)

st.title("📄 Recruiter Screener")

jd =
