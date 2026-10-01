import streamlit as st
import db
import ui

st.set_page_config(page_title="HireSmart", page_icon="💼", layout="wide")
db.init()
ui.style(top_nav=True)
ui.polish()

user = st.session_state.get("user")

if not user:
    left, right = st.columns([1.25, 1], gap="large")
    with left:
        ui.hero2("✨ AI-powered hiring",
                 "Get hired faster with HireSmart",
                 "Check your resume, match with the right jobs and track every application in one place.")
        s1, s2, s3 = st.columns(3)
        with s1:
            ui.stat("📄", "Resumes learned from", "2,484")
        with s2:
            ui.stat("🗂️", "Job categories", "24")
        with s3:
            ui.stat("🎯", "Classifier accuracy", "70.4%")
    with right:
        with st.container(border=True):
            st.markdown("### Welcome 👋")
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

    ui.section("Everything you need to get hired")
    f1, f2, f3 = st.columns(3, gap="medium")
    with f1:
        ui.card("📊", "ATS resume checker", "Get a score out of 100 and a clear list of what to fix.")
    with f2:
        ui.card("🎯", "Smart job matching", "See which jobs fit best, with matched and missing skills.")
    with f3:
        ui.card("🧑‍💼", "Ranked applicants", "Recruiters see candidates ranked by match score.")

    ui.section("See what you get")
    p1, p2 = st.columns([1, 1.3], gap="large")
    with p1:
        with st.container(border=True):
            st.caption("SAMPLE PREVIEW")
            ui.ring(82, "ATS score", 150)
    with p2:
        with st.container(border=True):
            st.caption("SAMPLE REPORT")
            ui.meter("Structure", 88)
            ui.meter("Content", 75)
            ui.meter("Job match", 82)
            ui.show("<b>Matched skills</b><br>" + ui.chips(["python", "sql", "excel", "tableau"], "ok"))
            ui.show("<b>Missing skills</b><br>" + ui.chips(["statistics"], "no"))

    ui.section("How it works")
    ui.steps([
        ("Upload your resume", "PDF, DOCX or TXT. We read the text and find your skills."),
        ("Get your ATS score", "See what is strong, what is missing and what to fix first."),
        ("Match and apply", "Jobs are ranked by fit. Apply in one click and track status."),
    ])

else:
    ui.nav(user)
    ui.hero2("👋 Dashboard", f"Welcome back, {user['name'].split()[0]}",
             f"Signed in as {user['role']}")

    if user["role"] == "candidate":
        apps = db.my_applications(user["id"])
        has_resume = bool(db.get_resume(user["id"]).strip())
        steps_done = [True, has_resume, len(apps) > 0]
        left, right = st.columns([1.4, 1], gap="large")
        with left:
            c1, c2, c3 = st.columns(3)
            with c1:
                ui.stat("📄", "Resume saved", "Yes" if has_resume else "Not yet")
            with c2:
                ui.stat("📨", "Applications", len(apps))
            with c3:
                ui.stat("⭐", "Shortlisted or later",
                        sum(a["status"] in ("Shortlisted", "Interview", "Hired") for a in apps))
            ui.section("Quick actions")
            a, b = st.columns(2)
            a.page_link("pages/1_Candidate_ATS_Checker.py", label="Check my resume", icon="📊")
            b.page_link("pages/2_Candidate_Jobs.py", label="Find and apply to jobs", icon="🎯")
        with right:
            with st.container(border=True):
                st.markdown("**Your profile checklist**")
                st.progress(sum(steps_done) / 3)
                st.write(("✅" if steps_done[0] else "⬜") + " Create your account")
                st.write(("✅" if steps_done[1] else "⬜") + " Save your resume")
                st.write(("✅" if steps_done[2] else "⬜") + " Apply to your first job")
    else:
        jobs = db.list_jobs(user["id"])
        total = sum(len(db.job_applicants(j["id"])) for j in jobs)
        c1, c2 = st.columns(2)
        with c1:
            ui.stat("💼", "Jobs posted", len(jobs))
        with c2:
            ui.stat("👥", "Total applicants", total)
        ui.section("Quick actions")
        a, b = st.columns(2)
        a.page_link("pages/3_Recruiter_Jobs.py", label="Post jobs and review applicants", icon="🧑‍💼")
        b.page_link("pages/4_Recruiter_Screener.py", label="Bulk resume screener", icon="📄")

ui.footer()
