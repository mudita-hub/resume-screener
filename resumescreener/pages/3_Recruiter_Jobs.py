import streamlit as st
import db
import ui
from core import require, match
from utils import clean, extract_skills, SKILLS

ui.style(top_nav=True, sidebar=False)
user = require("recruiter")
ui.nav(user)
ui.hero("Jobs and applicants", "Post jobs and review candidates ranked by match score.")

st.subheader("Post a new job")
with st.container(border=True):
    c1, c2 = st.columns(2)
    title = c1.text_input("Job title")
    company = c2.text_input("Company")
    desc = st.text_area("Job description", height=140)
    detected = extract_skills(clean(desc)) if desc.strip() else []
    must = st.multiselect("Must-have skills (auto-detected)", SKILLS, default=detected)
    if st.button("Post job", type="primary"):
        if title.strip() and desc.strip():
            db.add_job(user["id"], title, company, desc, must)
            st.toast("Job posted", icon="✅")
            st.rerun()
        else:
            st.warning("Enter a title and a description.")

st.subheader("My jobs and ranked applicants")
STATUSES = ["Applied", "Shortlisted", "Interview", "Rejected", "Hired"]
my_jobs = db.list_jobs(user["id"])
if not my_jobs:
    st.info("You have not posted any jobs yet.")

for j in my_jobs:
    apps = db.job_applicants(j["id"])
    with st.expander(f"{j['title']} · {j['company']} · {len(apps)} applicant(s)"):
        if not apps:
            st.caption("No applicants yet.")
        rows = [(match(a["resume_text"], j["description"], j["must"]), a) for a in apps]
        for m, a in sorted(rows, key=lambda x: x[0]["score"], reverse=True):
            with st.container(border=True):
                c1, c2, c3 = st.columns([3, 1.2, 2])
                with c1:
                    st.markdown(f"**{a['name']}**")
                    st.caption(a["email"])
                    ui.show(ui.chips(m["matched"], "ok") + ui.chips(m["missing"], "no"))
                with c2:
                    ui.ring(m["score"], "match", 90)
                with c3:
                    new = c3.selectbox("Status", STATUSES, index=STATUSES.index(a["status"]),
                                       key=f"st_{a['app_id']}")
                    if new != a["status"]:
                        db.set_status(a["app_id"], new)
                        st.rerun()
