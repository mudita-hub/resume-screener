import streamlit as st
import db
from core import require, match

user = require("candidate")
st.title("🔎 Jobs matched to your resume")

resume = db.get_resume(user["id"])
if not resume.strip():
    st.warning("Upload and save your resume on the ATS Checker page first.")
    st.stop()

jobs = db.list_jobs()
if not jobs:
    st.info("No jobs posted yet. Ask a recruiter account to post one.")
    st.stop()

applied = {a["job_id"] for a in db.my_applications(user["id"])}
scored = sorted(((match(resume, j["description"], j["must"]), j) for j in jobs),
                key=lambda x: x[0]["score"], reverse=True)

for m, j in scored:
    with st.expander(f"{j['title']} · {j['company']} · {m['score']}% match"):
        st.write(j["description"])
        st.markdown("**Matched skills:** " + (", ".join(m["matched"]) or "none"))
        st.markdown("**Missing skills:** " + (", ".join(m["missing"]) or "none 🎉"))
        if j["id"] in applied:
            st.success("You have applied.")
        elif st.button("Apply", key=f"apply_{j['id']}", type="primary"):
            db.apply_to_job(j["id"], user["id"])
            st.rerun()

st.subheader("My applications")
apps = db.my_applications(user["id"])
if apps:
    st.dataframe([{"Job": a["title"], "Company": a["company"], "Status": a["status"]} for a in apps],
                 use_container_width=True)
else:
    st.caption("No applications yet.")
