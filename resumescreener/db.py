import sqlite3, hashlib, secrets
from pathlib import Path

DB = Path(__file__).parent / "platform.db"


def conn():
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    return c


def init():
    with conn() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT UNIQUE, name TEXT,
            role TEXT, salt TEXT, pw TEXT, resume_text TEXT DEFAULT '');
        CREATE TABLE IF NOT EXISTS jobs(
            id INTEGER PRIMARY KEY AUTOINCREMENT, recruiter_id INTEGER, title TEXT,
            company TEXT, description TEXT, must TEXT,
            created TEXT DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS applications(
            id INTEGER PRIMARY KEY AUTOINCREMENT, job_id INTEGER, candidate_id INTEGER,
            status TEXT DEFAULT 'Applied', created TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(job_id, candidate_id));
        """)


def _hash(pw, salt):
    return hashlib.pbkdf2_hmac("sha256", pw.encode(), salt.encode(), 100_000).hex()


def create_user(name, email, pw, role):
    salt = secrets.token_hex(8)
    try:
        with conn() as c:
            c.execute("INSERT INTO users(email,name,role,salt,pw) VALUES(?,?,?,?,?)",
                      (email.strip().lower(), name.strip(), role, salt, _hash(pw, salt)))
        return True
    except sqlite3.IntegrityError:
        return False


def login(email, pw):
    with conn() as c:
        r = c.execute("SELECT * FROM users WHERE email=?", (email.strip().lower(),)).fetchone()
    if r and r["pw"] == _hash(pw, r["salt"]):
        return {"id": r["id"], "name": r["name"], "email": r["email"], "role": r["role"]}
    return None


def get_resume(uid):
    with conn() as c:
        r = c.execute("SELECT resume_text FROM users WHERE id=?", (uid,)).fetchone()
    return r["resume_text"] if r else ""


def set_resume(uid, text):
    with conn() as c:
        c.execute("UPDATE users SET resume_text=? WHERE id=?", (text, uid))


def add_job(rid, title, company, desc, must):
    with conn() as c:
        c.execute("INSERT INTO jobs(recruiter_id,title,company,description,must) VALUES(?,?,?,?,?)",
                  (rid, title, company, desc, ",".join(must)))


def list_jobs(recruiter_id=None):
    with conn() as c:
        if recruiter_id:
            rows = c.execute("SELECT * FROM jobs WHERE recruiter_id=? ORDER BY id DESC",
                             (recruiter_id,)).fetchall()
        else:
            rows = c.execute("SELECT * FROM jobs ORDER BY id DESC").fetchall()
    out = []
    for r in rows:
        d = dict(r)
        d["must"] = [s for s in d["must"].split(",") if s]
        out.append(d)
    return out


def apply_to_job(job_id, cid):
    try:
        with conn() as c:
            c.execute("INSERT INTO applications(job_id,candidate_id) VALUES(?,?)", (job_id, cid))
        return True
    except sqlite3.IntegrityError:
        return False


def my_applications(cid):
    with conn() as c:
        rows = c.execute("""SELECT a.job_id, a.status, j.title, j.company
                            FROM applications a JOIN jobs j ON j.id=a.job_id
                            WHERE a.candidate_id=? ORDER BY a.id DESC""", (cid,)).fetchall()
    return [dict(r) for r in rows]


def job_applicants(job_id):
    with conn() as c:
        rows = c.execute("""SELECT a.id AS app_id, a.status, u.name, u.email, u.resume_text
                            FROM applications a JOIN users u ON u.id=a.candidate_id
                            WHERE a.job_id=?""", (job_id,)).fetchall()
    return [dict(r) for r in rows]


def set_status(app_id, status):
    with conn() as c:
        c.execute("UPDATE applications SET status=? WHERE id=?", (status, app_id))
