import streamlit as st
import db
import ui
from core import require, ats_report
from utils import clean, extract_skills, read_file

ui.style(top_nav=True, sidebar=False)
ui.polish()
user = require("candidate")
ui.nav(user)
ui.hero("Resume checker", "Upload your resume and get an ATS score with a clear list of fixes.")

if "resume_text" not in st.session_state:
    st.session_state["resume_text"] = db.get_resume(user["id"])


def group_pct(checks, g):
    items = [c for c in checks if c["group"] == g]
    return 100 * sum(c["pts"] for c in items if c["ok"]) / sum(c["pts"] for c in items)


left, right = st.columns([1, 1.15], gap="large")

with left:
    with st.container(border=True):
        st.markdown("##### 1 · Upload your resume")
        f = st.file_uploader("Resume", type=["pdf", "docx", "txt"], label_visibility="collapsed")
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
            st.caption(f"Resume loaded: {len(resume.split())} words")
            if st.button("Save to my profile", use_container_width=True):
                db.set_resume(user["id"], resume)
                st.success("Saved. You can now apply to jobs.")

        st.markdown("##### 2 · Target job (optional)")
        jd = st.text_area("Job description", height=150, label_visibility="collapsed",
                          placeholder="Paste a job description to get a job-match score")
        detected = extract_skills(clean(jd)) if jd.strip() else []
        must = st.multiselect("Skills required by this job", detected, default=detected)
        go = st.button("Analyze my resume", type="primary", use_container_width=True)

if go:
    if not resume:
        st.warning("Upload a resume first.")
    else:
        with st.spinner("Analyzing..."):
            st.session_state["ats"] = ats_report(resume, jd, must)

with right:
    r = st.session_state.get("ats")
    if not r:
        with st.container(border=True):
            st.markdown("#### Your results will appear here")
            st.caption("Upload a resume and click Analyze to see your ATS score, section checks and fixes.")
    else:
        with st.container(border=True):
            ui.ring(r["score"], "ATS score", 150)
            ui.meter("Structure", group_pct(r["checks"], "Structure"))
            ui.meter("Content", group_pct(r["checks"], "Content"))
            if r["match"]:
                ui.meter("Job match", r["match"]["score"])
                ui.show("<b>Matched skills</b><br>" + (ui.chips(r["matched"], "ok") or "none"))
                ui.show("<b>Missing skills</b><br>" + (ui.chips(r["missing"], "no") or "none 🎉"))
        fixes = [c for c in r["checks"] if not c["ok"]]
        with st.container(border=True):
            st.markdown("#### Fix these first" if fixes else "#### Nothing to fix 🎉")
            for c in fixes:
                st.write("❌ " + c["tip"])
            if r["missing"]:
                st.write("➕ Add these skills if you really have them: " + ", ".join(r["missing"]))
            with st.expander("Full checklist"):
                for c in r["checks"]:
                    st.write(("✅ " if c["ok"] else "❌ ") + f"{c['label']} · {c['group']}")
