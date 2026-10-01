import streamlit as st
import db

st.set_page_config(page_title="HireSmart", page_icon="💼", layout="wide")
db.init()

st.title("💼 HireSmart: AI Hiring Platform")
st.caption("Candidates check and improve their resumes, apply to jobs and track status. "
           "Recruiters post jobs and get ranked applicants.")

user = st.session_state.get("user")

if user:
    st.success(f"Logged in as **{user['name']}** ({user['role']})")
    if user["role"] == "candidate":
        st.markdown("Use the sidebar: **Candidate ATS Checker** to score your resume, "
                    "**Candidate Jobs** to find and apply.")
    else:
        st.markdown("Use the sidebar: **Recruiter Jobs** to post jobs and review applicants, "
                    "**Recruiter Screener** for quick bulk screening.")
    if st.button("Log out"):
        st.session_state.clear()
        st.rerun()
else:
    t1, t2 = st.tabs(["🔑 Login", "📝 Register"])
    with t1:
        email = st.text_input("Email", key="l_email")
        pw = st.text_input("Password", type="password", key="l_pw")
        if st.button("Login", type="primary"):
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
        if st.button("Create account", type="primary"):
            if not name.strip() or "@" not in email2 or len(pw2) < 6:
                st.warning("Enter a name, a valid email and a password of 6+ characters.")
            elif db.create_user(name, email2, pw2, role):
                st.success("Account created. Now log in from the Login tab.")
            else:
                st.error("That email is already registered.")
    st.info("Demo project: data is stored in a local SQLite file and may reset when the app restarts.")
