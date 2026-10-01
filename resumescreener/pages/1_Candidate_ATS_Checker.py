import streamlit as st
import db
from core import require, ats_report
from utils import clean, extract_skills, read_file

user = require("candidate")
st.title("📊 ATS Resume Checker")

if "resume_text" not in st.session_state:
    st.session_state["resume_text"] = db.get_resume(user["id"])

f = st.file_uploader("Upload your resume (PDF, DOCX or TXT)", type=["pdf", "docx", "txt"])
if f:
    try:
        txt = read_file(f)
        if txt.strip():
            st.session_state["resume_text"] = txt
        else:
            st.warning("No text found. This may be a scanned PDF.")
    except Exception:
        st.error("Could not read that file.")

resume = st.session_state["resume_text"]
if resume:
    with st.expander("Extracted resume text"):
        st.text(resume[:3000])
    if st.button("💾 Save this resume to my profile"):
        db.set_resume(user["id"], resume)
        st.success("Saved. You can now apply to jobs.")

jd = st.text_area("Paste the job description (optional, gives a job-match score)", height=140)
detected = extract_skills(clean(jd)) if jd.strip() else []
must = st.multiselect("Skills required by this job", detected, default=detected)

if st.button("Check my resume", type="primary"):
    if not resume:
        st.warning("Upload a resume first.")
    else:
        st.session_state["ats"] = ats_report(resume, jd, must)

r = st.session_state.get("ats")
if r:
    st.metric("ATS score", f"{r['score']} / 100")
    st.progress(min(int(r["score"]), 100))
    if r["match"]:
        c1, c2 = st.columns(2)
        c1.markdown("**Matched skills:** " + (", ".join(r["matched"]) or "none"))
        c2.markdown("**Missing skills:** " + (", ".join(r["missing"]) or "none 🎉"))
    st.subheader("Checklist")
    for c in r["checks"]:
        st.write(("✅ " if c["ok"] else "❌ ") + f"{c['label']}  ·  {c['group']}")
    fixes = [c for c in r["checks"] if not c["ok"]]
    if fixes or r["missing"]:
        st.subheader("Fix these first")
        for c in fixes:
            st.write("• " + c["tip"])
        if r["missing"]:
            st.write("• Add these skills if you really have them: " + ", ".join(r["missing"]))
