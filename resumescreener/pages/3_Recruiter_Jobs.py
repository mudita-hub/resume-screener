import streamlit as st
import db
from core import require, match
from utils import clean, extract_skills, SKILLS

user = require("recruiter")
st.title("🧑‍💼 Recruiter: jobs and applicants")

st.subheader("Post a new job")
c1, c2 = st.columns(2)
title = c1.text_input("Job title")
company = c2.text_input("Company")
desc = st.text_area("Job description", height=140)
detected = extract_skills(clean(desc)) if desc.strip() else []
must = st.multiselect("Must-have skills (auto-detected)", SKILLS, default=detected)
if st.button("Post job", type="primary"):
    if title.strip() and desc.strip():
        db.add_job(user["id"], title, company, desc, must)
        st.success("Job posted.")
        st.rerun()
    else:
        st.warning("Enter a title and a description.")

st.subheader("My jobs and ranked applicants")
STATUSES = ["Applied", "Shortlisted", "Interview", "Rejected", "Hired"]
for j in db.list_jobs(user["id"]):
    apps = db.job_applicants(j["id"])
    with st.expander(f"{j['title']} · {j['company']} · {len(apps)} applicant(s)"):
        if not apps:
            st.caption("No applicants yet.")
        rows = [(match(a["resume_text"], j["description"], j["must"]), a) for a in apps]
        for m, a in sorted(rows, key=lambda x: x[0]["score"], reverse=True):
            c1, c2, c3 = st.columns([3, 2, 2])
            c1.markdown(f"**{a['name']}** ({a['email']})  \n"
                        f"Matched: {', '.join(m['matched']) or '-'}  \n"
                        f"Missing: {', '.join(m['missing']) or '-'}")
            c2.metric("Match", f"{m['score']}%")
            new = c3.selectbox("Status", STATUSES, index=STATUSES.index(a["status"]),
                               key=f"st_{a['app_id']}")
            if new != a["status"]:
                db.set_status(a["app_id"], new)
                st.rerun()
