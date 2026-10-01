import streamlit as st
import db
import ui

st.set_page_config(page_title="HireSmart", page_icon="💼", layout="wide")
db.init()
ui.style(top_nav=True)

user = st.session_state.get("user")

if not user:
    left, right = st.columns([1.2, 1], gap="large")
    with left:
        ui.hero("Get hired faster with HireSmart",
                "Check your resume, match with jobs and track every application in one place.")
        ui.features([
            ("📊", "ATS resume checker", "Get a score out of 100 and a clear list of what to fix."),
            ("🎯", "Smart job matching", "See which jobs fit best, with matched and missing skills."),
            ("🧑‍💼", "Ranked applicants", "Recruiters see candidates ranked by match score."),
        ])
    with right:
        with st.container(border=True):
            t1, t2 = st.tabs(["Login", "Register"])
            with t1:
                email = st.text_input("Email", key="l_email")
                pw = st.text_input("Password", type="password", key="l_pw")
                if st.button("Login", type="primary", use_container_width=True):
                    u = db.login(email, pw)
                    if u:
                        st.session_state["user"] = u
                        st.rerun()
                    else:
                        st.error("Wrong email or password.")
            with t2:
                name = st.text_input("Full name")
                email2 = st.text_input("Email", key="r_email")
                pw2 = st.text_input("Password (min 6 characters)", type="password", key="r_pw")
                role = st.radio("I am a", ["candidate", "recruiter"], horizontal=True)
                if st.button("Create account", type="primary", use_container_width=True):
                    if not name.strip() or "@" not in email2 or len(pw2) < 6:
                        st.warning("Enter a name, a valid email and a password of 6+ characters.")
                    elif db.create_user(name, email2, pw2, role):
                        st.success("Account created. Now log in from the Login tab.")
                    else:
                        st.error("That email is already registered.")
        st.caption("Demo project: data is stored in a local SQLite file and may reset when the app restarts.")

else:
    ui.nav(user)
    ui.hero(f"Welcome back, {user['name'].split()[0]}", f"Signed in as {user['role']}")

    if user["role"] == "candidate":
        apps = db.my_applications(user["id"])
        has_resume = bool(db.get_resume(user["id"]).strip())
        steps = [True, has_resume, len(apps) > 0]
        left, right = st.columns([1.4, 1], gap="large")
        with left:
            c1, c2, c3 = st.columns(3)
            c1.metric("Resume saved", "Yes" if has_resume else "Not yet")
            c2.metric("Applications", len(apps))
            c3.metric("Shortlisted or later",
                      sum(a["status"] in ("Shortlisted", "Interview", "Hired") for a in apps))
            st.subheader("Quick actions")
            a, b = st.columns(2)
            a.page_link("pages/1_Candidate_ATS_Checker.py", label="Check my resume", icon="📊")
            b.page_link("pages/2_Candidate_Jobs.py", label="Find and apply to jobs", icon="🎯")
        with right:
            with st.container(border=True):
                st.markdown("**Your profile checklist**")
                st.progress(sum(steps) / 3)
                st.write(("✅" if steps[0] else "⬜") + " Create your account")
                st.write(("✅" if steps[1] else "⬜") + " Save your resume")
                st.write(("✅" if steps[2] else "⬜") + " Apply to your first job")
    else:
        jobs = db.list_jobs(user["id"])
        total = sum(len(db.job_applicants(j["id"])) for j in jobs)
        c1, c2 = st.columns(2)
        c1.metric("Jobs posted", len(jobs))
        c2.metric("Total applicants", total)
        st.subheader("Quick actions")
        a, b = st.columns(2)
        a.page_link("pages/3_Recruiter_Jobs.py", label="Post jobs and review applicants", icon="🧑‍💼")
        b.page_link("pages/4_Recruiter_Screener.py", label="Bulk resume screener", icon="📄")
