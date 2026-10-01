from html import escape
import streamlit as st

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html, body, .stMarkdown, button, input, textarea, label {font-family: 'Inter', sans-serif;}
footer {visibility: hidden;}
header[data-testid="stHeader"] {background: transparent;}
.block-container {padding-top: 1.2rem; max-width: 1150px;}
.hero {padding: 30px 34px; border-radius: 20px; margin: 6px 0 22px;
       background: linear-gradient(135deg, #4f46e5, #7c3aed 60%, #db2777);}
.hero .t {color: #fff; font-size: 2rem; font-weight: 800; line-height: 1.2;}
.hero .s {color: #fff; opacity: .92; margin-top: 8px; font-size: 1.05rem;}
.feat {display: flex; gap: 14px; align-items: flex-start; padding: 14px 16px; margin-bottom: 10px;
       border-radius: 14px; border: 1px solid rgba(128,128,128,.28); background: #fff; color: #0f172a;}
.feat .i {font-size: 1.5rem;}
.feat .h {font-weight: 650; color: #0f172a;}
.feat .d {opacity: .75; font-size: .9rem; color: #0f172a;}
[data-testid="stMetric"] {border: 1px solid rgba(128,128,128,.25); border-radius: 14px;
                          padding: 12px 16px; background: rgba(128,128,128,.05);}
.chip {display: inline-block; padding: 3px 11px; margin: 3px 5px 3px 0; border-radius: 99px;
       font-size: .78rem; font-weight: 500;}
.chip.ok {background: rgba(22,163,74,.15); color: #16a34a; border: 1px solid rgba(22,163,74,.4);}
.chip.no {background: rgba(220,38,38,.12); color: #dc2626; border: 1px solid rgba(220,38,38,.4);}
.chip.kw {background: rgba(99,102,241,.14); color: #6366f1; border: 1px solid rgba(99,102,241,.4);}
.meter {margin: 10px 0;}
.meter .l {display: flex; justify-content: space-between; font-size: .85rem; font-weight: 600;}
.meter .b {height: 8px; border-radius: 99px; background: rgba(128,128,128,.22); overflow: hidden; margin-top: 5px;}
.meter .b div {height: 100%; border-radius: 99px;}
.pipe {display: flex; gap: 6px; flex-wrap: wrap; margin-top: 8px;}
.pipe span {padding: 4px 12px; border-radius: 99px; font-size: .8rem; font-weight: 600;
            background: rgba(128,128,128,.15); opacity: .7;}
.pipe span.done {background: rgba(22,163,74,.18); color: #16a34a; opacity: 1;}
.pipe span.cur {background: #6366f1; color: #fff; opacity: 1;}
.pipe span.bad {background: rgba(220,38,38,.15); color: #dc2626; opacity: 1;}
.brand {font-weight: 800; font-size: 1.2rem; padding-top: 6px;}
@media (max-width: 640px) {.hero .t {font-size: 1.5rem;} .hero {padding: 22px;}}
</style>
"""

POLISH = """
<style>
.stApp {background: linear-gradient(180deg, #f1efff 0%, #f8fafc 380px);}
@keyframes shift {0%{background-position:0% 50%} 50%{background-position:100% 50%} 100%{background-position:0% 50%}}
.hero, .hero2 {position: relative; overflow: hidden; border-radius: 24px; color: #fff;
  background: linear-gradient(120deg, #312e81, #6d28d9, #db2777, #6d28d9);
  background-size: 300% 300%; animation: shift 14s ease infinite;
  box-shadow: 0 18px 40px rgba(79,70,229,.28);}
.hero2 {padding: 40px 38px; margin: 6px 0 20px;}
.hero::after, .hero2::after {content: ""; position: absolute; right: -60px; top: -60px; width: 240px;
  height: 240px; border-radius: 50%; background: rgba(255,255,255,.10);}
.hero2 .t {font-size: 2.6rem; font-weight: 800; line-height: 1.12; margin-top: 14px; color: #fff;}
.hero2 .s {font-size: 1.1rem; opacity: .92; margin-top: 12px; max-width: 560px; color: #fff;}
.hero2 .pill {display: inline-block; padding: 5px 14px; border-radius: 99px; font-size: .8rem;
  font-weight: 600; background: rgba(255,255,255,.18); border: 1px solid rgba(255,255,255,.35); color: #fff;}
.fcard {background: #fff; border-radius: 18px; padding: 20px; height: 100%; color: #0f172a;
  border: 1px solid rgba(99,102,241,.15); box-shadow: 0 4px 16px rgba(15,23,42,.05);
  transition: transform .2s ease, box-shadow .2s ease;}
.fcard:hover {transform: translateY(-4px); box-shadow: 0 14px 30px rgba(79,70,229,.18);}
.fcard .ib {width: 46px; height: 46px; border-radius: 14px; display: flex; align-items: center;
  justify-content: center; font-size: 1.4rem; margin-bottom: 12px;
  background: linear-gradient(135deg, #e0e7ff, #fce7f3);}
.fcard .h {font-weight: 700; font-size: 1.05rem; color: #0f172a;}
.fcard .d {opacity: .72; font-size: .9rem; margin-top: 4px; color: #0f172a;}
.stat {border-radius: 16px; padding: 18px 20px; background: #fff; color: #0f172a;
  border: 1px solid rgba(99,102,241,.18); box-shadow: 0 2px 10px rgba(15,23,42,.04);}
.stat .si {font-size: 1.5rem;}
.stat .sv {font-size: 1.8rem; font-weight: 800; color: #4f46e5; line-height: 1.2;}
.stat .sl {font-size: .85rem; opacity: .7; font-weight: 500; color: #0f172a;}
.step {padding: 18px; border-radius: 16px; background: #eef2ff; height: 100%; color: #0f172a;}
.step .n {display: inline-flex; width: 30px; height: 30px; border-radius: 50%;
  background: #4f46e5; color: #fff; align-items: center; justify-content: center;
  font-weight: 700; margin-bottom: 8px;}
.step .h {font-weight: 700; color: #0f172a;}
.step .d {opacity: .75; font-size: .9rem; margin-top: 2px; color: #0f172a;}
.stButton > button[kind="primary"], .stDownloadButton > button[kind="primary"] {
  background: linear-gradient(135deg, #4f46e5, #7c3aed 60%, #db2777); border: none; color: #fff;
  box-shadow: 0 6px 18px rgba(79,70,229,.32); padding: .55rem 1.1rem;}
.stButton > button[kind="primary"]:hover {filter: brightness(1.08); transform: translateY(-1px);}
.stButton > button {transition: all .15s ease; border-radius: 12px; font-weight: 600;}
[data-baseweb="tab-list"] {gap: 6px;}
[data-baseweb="tab"] {font-weight: 600; border-radius: 99px; padding: 6px 16px;}
[data-baseweb="input"], [data-baseweb="textarea"], [data-baseweb="select"] > div {border-radius: 12px;}
[data-testid="stVerticalBlockBorderWrapper"] {background: #fff; border-radius: 18px;
  box-shadow: 0 4px 16px rgba(15,23,42,.05); transition: box-shadow .2s ease;}
[data-testid="stVerticalBlockBorderWrapper"]:hover {box-shadow: 0 12px 28px rgba(15,23,42,.10);}
[data-testid="stPageLink"] a {border: 1px solid rgba(99,102,241,.25); border-radius: 12px;
  background: #fff; transition: all .15s ease;}
[data-testid="stPageLink"] a:hover {background: #eef2ff; border-color: #6366f1;}
.sec {font-size: 1.5rem; font-weight: 800; margin: 28px 0 12px; color: #0f172a;}
.foot {text-align: center; opacity: .55; font-size: .82rem; margin: 36px 0 8px;}
@media (max-width: 640px) {.hero2 {padding: 26px 22px;} .hero2 .t {font-size: 1.7rem;}}
</style>
"""


def style(top_nav=False, sidebar=True):
    st.markdown(CSS, unsafe_allow_html=True)
    extra = ""
    if top_nav:
        extra += '[data-testid="stSidebarNav"]{display:none;}'
    if not sidebar:
        extra += ('[data-testid="stSidebar"],[data-testid="stSidebarCollapsedControl"],'
                  '[data-testid="collapsedControl"]{display:none;}')
    if extra:
        st.markdown(f"<style>{extra}</style>", unsafe_allow_html=True)


def polish():
    st.markdown(POLISH, unsafe_allow_html=True)


def show(html):
    st.markdown(html, unsafe_allow_html=True)


def color(score):
    return "#16a34a" if score >= 70 else ("#d97706" if score >= 45 else "#dc2626")


def hero(title, subtitle):
    show(f'<div class="hero"><div class="t">{title}</div><div class="s">{subtitle}</div></div>')


def hero2(badge, title, subtitle):
    show(f'<div class="hero2"><span class="pill">{badge}</span>'
         f'<div class="t">{title}</div><div class="s">{subtitle}</div></div>')


def features(items):
    for icon, head, desc in items:
        show(f'<div class="feat"><div class="i">{icon}</div>'
             f'<div><div class="h">{head}</div><div class="d">{desc}</div></div></div>')


def card(icon, head, desc):
    show(f'<div class="fcard"><div class="ib">{icon}</div>'
         f'<div class="h">{head}</div><div class="d">{desc}</div></div>')


def section(text):
    show(f'<div class="sec">{text}</div>')


def stat(icon, label, value):
    show(f'<div class="stat"><div class="si">{icon}</div>'
         f'<div class="sv">{value}</div><div class="sl">{label}</div></div>')


def steps(items):
    cols = st.columns(len(items))
    for i, (col, (head, desc)) in enumerate(zip(cols, items), 1):
        col.markdown(f'<div class="step"><div class="n">{i}</div><div class="h">{head}</div>'
                     f'<div class="d">{desc}</div></div>', unsafe_allow_html=True)


def footer():
    show('<div class="foot">Built with Streamlit, scikit-learn (TF-IDF + LinearSVC). '
         'Scores are a guide, a human should make the final decision.</div>')


def chips(items, kind="ok"):
    if not items:
        return ""
    return "".join(f'<span class="chip {kind}">{escape(str(s))}</span>' for s in items)


def meter(label, pct):
    pct = max(0, min(100, float(pct)))
    c = color(pct)
    show(f'<div class="meter"><div class="l"><span>{label}</span><span>{pct:.0f}%</span></div>'
         f'<div class="b"><div style="width:{pct}%;background:{c}"></div></div></div>')


def ring(score, label="score", size=140):
    c = color(score)
    r = int(size * 0.09)
    show(
        f'<div style="display:flex;justify-content:center;margin:6px 0 10px">'
        f'<div style="position:relative;width:{size}px;height:{size}px">'
        f'<div style="width:100%;height:100%;border-radius:50%;'
        f'background:conic-gradient({c} {score}%, rgba(128,128,128,.22) 0);'
        f'-webkit-mask:radial-gradient(farthest-side,transparent calc(100% - {r}px),#000 calc(100% - {r - 1}px));'
        f'mask:radial-gradient(farthest-side,transparent calc(100% - {r}px),#000 calc(100% - {r - 1}px));"></div>'
        f'<div style="position:absolute;inset:0;display:flex;flex-direction:column;'
        f'align-items:center;justify-content:center">'
        f'<div style="font-size:{int(size * 0.28)}px;font-weight:800;color:{c};line-height:1">{score:.0f}</div>'
        f'<div style="font-size:.72rem;opacity:.7">{label}</div></div></div></div>')


def pipeline(status):
    stages = ["Applied", "Shortlisted", "Interview", "Hired"]
    if status == "Rejected":
        show('<div class="pipe"><span class="done">Applied</span><span class="bad">Rejected</span></div>')
        return
    idx = stages.index(status) if status in stages else 0
    parts = []
    for i, s in enumerate(stages):
        cls = "done" if i < idx else ("cur" if i == idx else "")
        parts.append(f'<span class="{cls}">{s}</span>')
    show('<div class="pipe">' + "".join(parts) + "</div>")


def nav(user):
    if user["role"] == "candidate":
        items = [("app.py", "Home", "🏠"),
                 ("pages/1_Candidate_ATS_Checker.py", "Resume checker", "📊"),
                 ("pages/2_Candidate_Jobs.py", "Jobs", "🎯")]
    else:
        items = [("app.py", "Home", "🏠"),
                 ("pages/3_Recruiter_Jobs.py", "Jobs and applicants", "🧑‍💼"),
                 ("pages/4_Recruiter_Screener.py", "Bulk screener", "📄")]
    cols = st.columns([1.3] + [1.4] * len(items) + [0.9])
    cols[0].markdown('<div class="brand">💼 HireSmart</div>', unsafe_allow_html=True)
    for col, (path, label, icon) in zip(cols[1:-1], items):
        col.page_link(path, label=label, icon=icon)
    if cols[-1].button("Log out", use_container_width=True):
        st.session_state.clear()
        st.rerun()
