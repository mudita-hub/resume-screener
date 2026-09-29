import json
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
import streamlit as st
from sklearn.metrics.pairwise import cosine_similarity
from utils import clean, extract_skills, read_file, SKILLS

st.set_page_config(page_title="AI Resume Screener", page_icon="📄", layout="wide")

BASE = Path(__file__).parent

@st.cache_resource
def load_artifacts():
    tfidf = joblib.load(BASE / "artifacts" / "tfidf.pkl")
    clf = joblib.load(BASE / "artifacts" / "clf.pkl")
    db = pd.read_csv(BASE / "artifacts" / "resumes_db.csv")
    db["clean"] = db["clean"].fillna("")
    metrics = json.load(open(BASE / "artifacts" / "metrics.json"))
    db_vecs = tfidf.transform(db["clean"])
    return tfidf, clf, db, db_vecs, metrics

tfidf, clf, db, db_vecs, metrics = load_artifacts()

def rank(jd, cleaned_texts, required, w_text):
    """Return sim, skill %, final score, matched skills for each resume."""
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

# ---------- Sidebar ----------
st.sidebar.title("⚙️ Settings")
w_text = st.sidebar.slider("Weight: text similarity vs skill match", 0.0, 1.0, 0.6, 0.05,
                           help="1.0 = only text similarity, 0.0 = only skill match")
top_n = st.sidebar.number_input("Shortlist size", 1, 50, 10)
min_score = st.sidebar.slider("Minimum final score (%)", 0, 100, 0)

st.title("📄 AI Resume Screening & Candidate Shortlisting")

# ---------- Job description ----------
jd = st.text_area("Paste the job description", height=180,
                  placeholder="e.g. We are hiring a Data Analyst with SQL, Python, Excel, Tableau...")
jd_skills = extract_skills(clean(jd)) if jd else []
required = st.multiselect("Required skills (auto-detected from the JD, edit freely)",
                          SKILLS, default=jd_skills)

tab1, tab2, tab3 = st.tabs(["📤 Screen uploaded resumes", "🗂️ Search resume database", "📊 Model info"])

# ---------- Tab 1: uploaded resumes ----------
with tab1:
    files = st.file_uploader("Upload resumes (PDF or TXT)", type=["pdf", "txt"],
                             accept_multiple_files=True)
    if st.button("Screen candidates", type="primary", key="screen_upload"):
        if not jd.strip():
            st.warning("Please paste a job description first.")
        elif not files:
            st.warning("Please upload at least one resume.")
        else:
            names, cleaned = [], []
            for f in files:
                try:
                    txt = read_file(f)
                except Exception:
                    st.error(f"Could not read {f.name}")
                    continue
                if not txt.strip():
                    st.warning(f"No text found in {f.name} (scanned PDF?). Skipped.")
                    continue
                names.append(f.name)
                cleaned.append(clean(txt))
            if cleaned:
                sim, pct, final, matched, vecs = rank(jd, cleaned, required, w_text)
                out = pd.DataFrame({
                    "Candidate": names,
                    "Predicted category": clf.predict(vecs),
                    "Text similarity %": (sim * 100).round(1),
                    "Skill match %": (pct * 100).round(1),
                    "Final score": (final * 100).round(1),
                    "Matched skills": [", ".join(m) for m in matched],
                    "Missing skills": [", ".join(s for s in required if s not in m) for m in matched],
                })
                out = out[out["Final score"] >= min_score] \
                    .sort_values("Final score", ascending=False).head(int(top_n)).reset_index(drop=True)
                out.index += 1
                st.success(f"Shortlisted {len(out)} of {len(names)} candidates")
                st.dataframe(out, use_container_width=True)
                st.bar_chart(out.set_index("Candidate")["Final score"])
                st.download_button("⬇️ Download shortlist (CSV)", out.to_csv().encode(),
                                   "shortlist.csv", "text/csv")

# ---------- Tab 2: database search ----------
with tab2:
    cats = ["All"] + sorted(db["Category"].unique())
    cat = st.selectbox("Filter by category", cats)
    if st.button("Search database", type="primary", key="search_db"):
        if not jd.strip():
            st.warning("Please paste a job description first.")
        else:
            sub = db if cat == "All" else db[db["Category"] == cat]
            sim, pct, final, matched, _ = rank(jd, sub["clean"].tolist(), required, w_text)
            res = sub.assign(**{
                "Text similarity %": (sim * 100).round(1),
                "Skill match %": (pct * 100).round(1),
                "Final score": (final * 100).round(1),
                "Matched skills": [", ".join(m) for m in matched],
            })
            res = res[res["Final score"] >= min_score] \
                .sort_values("Final score", ascending=False).head(int(top_n))
            for _, r in res.iterrows():
                with st.expander(f"ID {r['ID']} · {r['Category']} · score {r['Final score']}"):
                    st.write(f"**Matched skills:** {r['Matched skills'] or '—'}")
                    st.caption(r["preview"] + "...")
            st.download_button("⬇️ Download results (CSV)",
                               res.drop(columns=["clean"]).to_csv(index=False).encode(),
                               "db_shortlist.csv", "text/csv")

# ---------- Tab 3: model info ----------
with tab3:
    st.metric("Held-out classifier accuracy", f"{metrics['accuracy']*100:.1f}%")
    rep = pd.DataFrame(metrics["report"]).T.drop(["accuracy"], errors="ignore")
    st.dataframe(rep.round(2), use_container_width=True)
    st.markdown("""
**How scoring works:** Final score = *w* × TF-IDF cosine similarity between the JD and resume
+ (1 − *w*) × fraction of required skills found in the resume.

**Limitations:** Scores reflect keyword and text overlap, not real candidate quality.
Scanned (image-only) PDFs can't be read. Automated screening can reflect bias in its data,
so a human should always review the shortlist.
""")
