from html import escape
import streamlit as st
import db
import ui
from core import require, match

ui.style(top_nav=True, sidebar=False)
ui.polish()
user = require("candidate")
ui.nav(user)
ui.hero("Jobs for you", "Ranked by how well your resume matches each role.")

resume = db.get_resume(user["id"])
if not resume.strip():
    st.warning("Save your resume on the Resume checker page first.")
    st.page_link("pages/1_Candidate_ATS_Checker.py", label="Go to Resume checker", icon="📊")
    st.stop()

tab_jobs, tab_apps = st.tabs(["Recommended jobs", "My applications"])

with tab_jobs:
    jobs = db.list_jobs()
    if not jobs:
        st.info("No jobs posted yet. Ask a recruiter account to post one.")
    else:
        f1, f2 = st.columns([2, 1])
        q = f1.text_input("Search", placeholder="Search by title or company", label_visibility="collapsed")
        min_m = f2.slider("Minimum match", 0, 100, 0)
        applied = {a["job_id"] for a in db.my_applications(user["id"])}
        scored = []
        for j in jobs:
            if q and q.lower() not in (j["title"] + " " + (j["company"] or "")).lower():
                continue
            m = match(resume, j["description"], j["must"])
            if m["score"] >= min_m:
                scored.append((m, j))
        scored.sort(key=lambda x: x[0]["score"], reverse=True)
        st.caption(f"{len(scored)} job(s) found")
        for m, j in scored:
            with st.container(border=True):
                c1, c2 = st.columns([4, 1])
                with c1:
                    st.markdown(f"### {escape(j['title'])}")
                    st.caption(escape(j["company"] or ""))
                    ui.show(ui.chips(m["matched"], "ok") + ui.chips(m["missing"], "no"))
                with c2:
                    ui.ring(m["score"], "match", 100)
                with st.expander("Job description"):
                    st.write(j["description"])
                if j["id"] in applied:
                    st.success("You have applied")
                elif st.button("Apply now", key=f"apply_{j['id']}", type="primary"):
                    db.apply_to_job(j["id"], user["id"])
                    st.toast("Application sent", icon="✅")
                    st.rerun()

with tab_apps:
    apps = db.my_applications(user["id"])
    if not apps:
        st.info("No applications yet. Apply to a job from the Recommended jobs tab.")
    for a in apps:
        with st.container(border=True):
            st.markdown(f"**{escape(a['title'])}**")
            st.caption(escape(a["company"] or ""))
            ui.pipeline(a["status"])
